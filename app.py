from fastapi import FastAPI, Depends, HTTPException, Response, Header, Request, Cookie
from fastapi.responses import JSONResponse
from typing import Annotated
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from utils import Core, Login
from utils.structures import LabelIntent, LabelStructure, CustomerStructure
from utils.database import actions
from utils import email2fa
import json
import secrets
import string
import stripe
stripe.api_key = 'sk_test_51Jq8nbLkbF66aoAo4HIXe1zSf2gSr8FP4U3rVZe6qRGY2xOWBbNYS7QYhamnqMdIpNU5KjQykWwNg7phUdsxv4Lt0040kembfC'

app = FastAPI()

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


awaiting_2fa = {}


class UserInDB(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ItemPayload(BaseModel):
    item_name: str
    item_description: str


class AccountCreate(BaseModel):
    email: str
    name: str
    password: str


class LabelStructureCreate(BaseModel):
    fromname: str
    fromcompany: str
    fromstreet: str
    fromstreet2: str
    fromzip: str
    fromcity: str
    fromstate: str
    fromphone: str
    toname: str
    tocompany: str
    tostreet: str
    tostreet2: str
    tozip: str
    tocity: str
    tostate: str
    tophone: str
    packageweight: str
    length: str
    width: str
    height: str
    description: str
    reference1: str
    reference2: str
    signature: str
    saturday: str
    price: str


class PricePayload(BaseModel):
    new_price: int


class GivePayload(BaseModel):
    amount: int
    user: str


class LabelId(BaseModel):
    labelid: str


class PlugType(BaseModel):
    plug: str


class PaymentIntentMod(BaseModel):
    amount: int
    user: str


class EmailReset(BaseModel):
    email: str


class EmailConfirm(BaseModel):
    email: str
    facode: str


class InvoiceSettings(BaseModel):
    custom_fields: Optional[dict]
    default_payment_method: Optional[str]
    footer: Optional[str]
    rendering_options: Optional[dict]


class CustomerData(BaseModel):
    id: str
    object: str
    address: Optional[str]
    balance: int
    created: int
    currency: Optional[str]
    default_currency: Optional[str]
    default_source: Optional[str]
    delinquent: bool
    description: Optional[str]
    discount: Optional[str]
    email: str
    invoice_prefix: str
    invoice_settings: Optional[InvoiceSettings]
    livemode: bool
    metadata: dict
    name: Optional[str]
    next_invoice_sequence: int
    phone: Optional[str]
    preferred_locales: list
    shipping: Optional[str]
    tax_exempt: str
    test_clock: Optional[str]


class CustomerCreatedEvent(BaseModel):
    id: str
    object: str
    account: str
    api_version: str
    created: int
    data: CustomerData
    livemode: bool
    pending_webhooks: int
    request: dict
    type: str


class AutomationPayload(BaseModel):
    cookie: str
    csrf: str


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(email: str, password: str):
    result = Login(email, password).request_login()
    return result


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        return CustomerStructure(payload['id'], payload['name'], payload['email'])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token has expired")


@app.post("/login", response_model=Token)
async def login_for_access_token(user: UserInDB):
    attempt = authenticate_user(user.email, user.password)
    if not attempt:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": attempt.customerEmail, "name": attempt.customerName, "id": attempt.customerId},
        expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/create_account")
async def create_account(payload: AccountCreate):
    if actions.fetch_user(payload.email):
        return {"success": False}
    result = actions.add_user(payload.email, payload.name, payload.email, payload.password)
    return {"success": result}


@app.get("/get_current_price")
async def get_price(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    result = await core.admin_get_price()
    return {"result": result}


@app.post("/set_current_price")
async def set_price(
        payload: PricePayload,
        authorization: str = Header(None),
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    result = await core.admin_set_price(payload.new_price)
    return {"result": result}


@app.post("/give_credits")
async def give_credits(
        payload: GivePayload,
        authorization: str = Header(None)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    result = await core.admin_give_user_credits(payload.user, payload.amount)
    return {"result": result}


@app.post("/order_labels")
async def order_labels(
        payload: list[LabelStructureCreate],
        authorization: str = Header(None)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    label_instances = [LabelStructure(**order.dict()) for order in payload]
    intent = LabelIntent(customerStruct, label_instances)
    result = await core.order_labels(intent)
    return {"result": result}


@app.post("/get_label_pdf")
async def get_label_pdf(
        payload: LabelId,
        authorization: str = Header(None)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    try:
        with open(rf"PDFs\{payload.labelid}.pdf", "rb") as file:
            content = file.read()
    except FileNotFoundError:
        content = ''
    return {"raw": content}


@app.get("/get_balance")
async def get_balance(
        authorization: str = Header(None)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    result = await core.check_credits()
    return {"result": result}


@app.get("/get_orders")
async def get_orders(
        authorization: str = Header(None)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    result = await core.get_orders()
    return {"result": result}


@app.post("/get_order_by_batch")
async def get_batch_order(
        payload: LabelId,
        authorization: str = Header(None)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    result = await core.get_orders(specified_order=payload.labelid)
    return {"result": result}


@app.get("/get_total_deposited")
async def get_total_deposited(
        authorization: str = Header(None)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    result = await core.get_total_deposited()
    return {"result": result}


@app.get("/get_plugs")
async def get_plugs(
        authorization: str = Header(None)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    result = await core.admin_get_plugs()
    return {"result": result}


@app.post("/set_plug")
async def set_plug(
        payload: PlugType,
        authorization: str = Header(None)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    result = await core.admin_set_current_plug(payload.plug)
    return {"result": result}


@app.get("/get_current_plug")
async def get_current_plug(
        authorization: str = Header(None)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    result = await core.admin_get_current_plugs()
    return {"result": result}


@app.get("/get_all_sales_history")
async def get_sales_history(
        authorization: str = Header(None)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    result = await core.admin_get_sales()
    return {"result": result}


@app.post("/automation/generate_labels")
async def set_plug(
        payload: AutomationPayload,
        authorization: str = Header(None)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.replace("Bearer ", "")
    customerStruct = decode_access_token(token)
    core = Core(customerStruct)
    customers_cookie = payload.cookie
    # not needed for this particular gen
    customers_csrf = payload.csrf
    # in core, start thread for label gen and save to DB, return here
    return {"success": True}


@app.post("/create_buy_intent")
async def create_payment(
        payload: PaymentIntentMod
):
    try:
        amount = payload.amount
        user = payload.user
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            payment_method_types=["card"],
            metadata={
                "user_purchasing": user,
                "amount_purchased": amount
            }
        )
        return jsonify({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 403


@app.post("/2fa_send")
async def email_send(
        payload: EmailReset
):
    users_email = payload.email
    try:
        sent_code = email2fa.send_mail(users_email)
    except:
        return {"success": False}
    awaiting_2fa[users_email] = sent_code
    return {"success": False}


@app.post("/2fa_confirm")
async def email_confirm(
        payload: EmailConfirm
):
    users_email = payload.email
    users_email_code = payload.facode
    if awaiting_2fa.get(users_email) != users_email_code:
        return {"success": False}
    del awaiting_2fa[users_email]
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    actions.change_user_password(users_email, password)
    return {"success": password}


@app.post("/stripe_webhook")
async def webhook_received(
        request: Request,
        stripe_signature: str = Header(None)
):
    webhook_secret = 'whsec_f10f858c9fa3d13a1287c5dceb6ab01040e399ea82ab164a2fbcf096c7fff91c'
    data = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload=data,
            sig_header=stripe_signature,
            secret=webhook_secret
        )
        event_data = event['data']
    except Exception as e:
        return {"error": str(e)}
    meta = event_data['object']['metadata']
    amount_owed = meta['amount_purchased']
    user = meta['user_purchasing']
    current_balance = actions.fetch_user_bal(user)
    actions.set_user_bal(amount_owed + current_balance)
    return {"status": "success"}


# stripe listen --forward-to localhost:8000/stripe_webhook
# uvicorn app:app --host localhost
