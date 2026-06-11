import pandas as pd
import joblib

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel

from api.fastapi_utils import Oauth2ClientCredentials
from api.keycloak_utils import get_keycloak_data
from keycloak.uma_permissions import AuthStatus

app = FastAPI()

pipeline = joblib.load("models/pipeline.pkl")

keycloak_openid, token_endpoint = get_keycloak_data()

oauth2_scheme = Oauth2ClientCredentials(
    tokenUrl=token_endpoint
)


class CarFeatures(BaseModel):
    Brand: str
    model: str
    Year: int
    kmDriven: float
    Transmission: str
    Owner: str
    FuelType: str


async def get_token_status(token: str) -> AuthStatus:
    return keycloak_openid.has_uma_access(
        token,
        "infer_endpoint#doInfer"
    )


async def check_token(
    token: str = Depends(oauth2_scheme)
) -> None:
    auth_status = await get_token_status(token)

    is_logged = auth_status.is_logged_in
    is_authorized = auth_status.is_authorized

    if not is_logged:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not is_authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}


@app.post("/predictions")
async def predictions(
    instance: CarFeatures,
    token: str = Depends(check_token)
):
    df = pd.DataFrame([instance.dict()])

    prediction = pipeline.predict(df)

    return {
        "predicted_price": float(prediction[0])
    }