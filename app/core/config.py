from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    demo_driver_token: str = "driver-demo-token"
    demo_customer_token: str = "customer-demo-token"
    demo_driver_id: str = "driver-1"
    demo_customer_id: str = "customer-1"
    demo_order_id: str = "order-1"
    location_ttl_seconds: int = 30
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
