from db.services import (
    create_database,
    database_session,
    user_service as user_service,
    category_service as category_service,
    budget_service as budget_service,
    financial_record_service as financial_record_service,
    dashboard_service as dashboard_service
)

from db.schemas import (
    user_schema as user_schema,
    category_schema as category_schema,
    budget_schema as budget_schema,
    financial_record_schema as financial_record_schema,
    dashboard_schema as dashboard_schema
)

import jwt as _jwt
import fastapi as _fastapi
import fastapi.security as _security
from fastapi import BackgroundTasks
from fastapi import UploadFile
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy.orm as _orm
import datetime
import os

app = _fastapi.FastAPI()

create_database.create_database()

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def root():
    return {'Status': 'OK'}


@app.get('/health', tags=['Health'])
async def health():
    return {'Status': '200 OK'}


@app.post('/api/register', response_model=user_schema.UserCreate, tags=['User'])
async def create_user(
        user: user_schema.UserCreate,
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    db_user = await user_service.get_user_by_email(db, user.email)
    if db_user:
        raise _fastapi.HTTPException(
            status_code=400,
            detail='Email already registered'
        )

    user = await user_service.create_user(db, user)
    return user

    # TODO: Send email to user
    # TODO: Fix 500 error from create_token due to UserCreate model instead of User model
    # return await user_service.create_token(user)


@app.post('/api/login', tags=['User'])
async def genetate_token(
        form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
        db: _orm.Session = _fastapi.Depends(database_session.database_session)
):
    user = await user_service.authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if not user:
        raise _fastapi.HTTPException(
            status_code=401,
            detail='Incorrect email or password'
        )

    return await user_service.create_token(user)


@app.post('/api/logout', tags=['User'])
async def logout(
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
):
    return {'Status': 'OK'}


@app.get('/api/users/me', response_model=user_schema.User, tags=['User'])
async def get_user(
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
):
    return user

@app.get('/api/users/verify/{email}/{token}', tags=['User'])
async def verify_user(
    email: str,
    token: str,
    db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    if not await user_service.verify_user(db, email, token):
        raise _fastapi.HTTPException(
            status_code=403,
            detail='Invalid'
        )


    return {'Status': 'OK'}


@app.post('/api/users/verify', tags=['User'])
async def verify_user(
        activation: user_schema.UserActivation,
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    if not await user_service.verify_user(db, activation.email, activation.token):
        raise _fastapi.HTTPException(
            status_code=403,
            detail='Invalid'
        )

    return {'Status': 'OK'}


@app.get('/api/categories', response_model=list[category_schema.Category], tags=['Category'])
async def get_categories(
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        skip: int = 0,
        limit: int = 100,
        db: _orm.Session = _fastapi.Depends(database_session.database_session)
):
    return await category_service.get_categories(db, user, skip, limit)


@app.get('/api/categories/{category_id}', response_model=category_schema.Category, tags=['Category'])
async def get_category_by_id(
        category_id: int,
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await category_service.get_category_by_id(db, user, category_id)


@app.post('/api/categories', response_model=category_schema.Category, tags=['Category'])
async def create_category(
        category: category_schema.CategoryCreate,
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await category_service.create_category(db, user, category)


@app.put('/api/categories/{category_id}', response_model=category_schema.Category, tags=['Category'])
async def update_category(
        category_id: int,
        category: category_schema.CategoryUpdate,
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await category_service.update_category(db, user, category_id, category)


@app.delete('/api/categories/{category_id}', response_model=category_schema.Category, tags=['Category'])
async def delete_category(
        category_id: int,
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await category_service.delete_category(db, user, category_id)


@app.get('/api/budget', response_model=list[budget_schema.Budget], tags=['Budget'])
async def get_budget(
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        skip: int = 0,
        limit: int = 100,
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await budget_service.get_budget(db, user)


@app.get('/api/budget/{budget_id}', response_model=budget_schema.Budget, tags=['Budget'])
async def get_category_by_id(
        budget_id: int,
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await budget_service.get_budget_by_id(db, user, budget_id)


@app.post('/api/budget', response_model=budget_schema.Budget, tags=['Budget'])
async def create_budget(
        budget: budget_schema.BudgetCreate,
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await budget_service.create_budget(db, user, budget)


@app.put('/api/budget/{budget_id}', response_model=budget_schema.Budget, tags=['Budget'])
async def update_budget(
        budget_id: int,
        budget: budget_schema.BudgetUpdate,
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await budget_service.update_budget(db, user, budget_id, budget)


@app.delete('/api/budget/{budget_id}', response_model=budget_schema.Budget, tags=['Budget'])
async def delete_budget(
        budget_id: int,
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await budget_service.delete_budget(db, user, budget_id)


@app.get('/api/financial-record', response_model=dict, tags=['Financial Record'])
async def get_financial_records(
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        skip: int = 0,
        limit: int = 100,
        query: str = None,
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
        start_date: datetime.date = datetime.date.today().replace(day=1)
):
    return await financial_record_service.get_financial_records(db, user, skip, limit, query, start_date)


@app.get('/api/financial-record-by-category', response_model=list[financial_record_schema.FinancialRecord],
         tags=['Financial Record'])
async def get_financial_records_by_category(
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        skip: int = 0,
        limit: int = 100,
        category_id: int = 0,
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
        start_date: datetime.date = datetime.date.today().replace(day=1)
):
    return await financial_record_service.get_financial_records_by_category(db, user, category_id, skip, limit,
                                                                            start_date)


@app.post('/api/financial-record', response_model=financial_record_schema.FinancialRecord, tags=['Financial Record'])
async def create_financial_record(
        financial_record: financial_record_schema.FinancialRecordCreate,
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await financial_record_service.create_financial_record(db, user, financial_record)


@app.post('/api/financial-record/mass-category-assigment', response_model=list[financial_record_schema.FinancialRecord],
          tags=['Financial Record'])
async def assign_financial_records(
        financial_records: financial_record_schema.FinancialRecordMassCategoryAssignment,
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await financial_record_service.assign_financial_records(db, user, financial_records)


@app.put('/api/financial-record/{financial_record_id}', response_model=financial_record_schema.FinancialRecord,
         tags=['Financial Record'])
async def update_financial_record(
        financial_record_id: int,
        financial_record: financial_record_schema.FinancialRecordUpdate,
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await financial_record_service.put_financial_record(db, user, financial_record_id, financial_record)


@app.delete('/api/financial-record/{financial_record_id}', response_model=financial_record_schema.FinancialRecordDelete,
            tags=['Financial Record'])
async def delete_financial_record(
        financial_record_id: int,
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await financial_record_service.delete_financial_record(db, user, financial_record_id)


@app.post('/api/mbank/import_csv', response_model=list[financial_record_schema.FinancialRecordCreate],
          tags=['Financial Records Import'])
async def import_mbank(
        file: _fastapi.UploadFile = _fastapi.File(...),
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await financial_record_service.import_mbank_csv(db, user, file)


@app.post('/api/pkobp/import_pdf', response_model=list[financial_record_schema.FinancialRecordCreate],
          tags=['Financial Records Import'])
async def import_pkobp(
        file: _fastapi.UploadFile = _fastapi.File(...),
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await financial_record_service.import_pkobp_pdf(db, user, file)


@app.post('/api/santander/import_csv', response_model=list[financial_record_schema.FinancialRecordCreate],
          tags=['Financial Records Import'])
async def import_santander(
        file: _fastapi.UploadFile = _fastapi.File(...),
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await financial_record_service.import_santander_csv(db, user, file)


@app.post('/api/pekaosa/import_csv', response_model=list[financial_record_schema.FinancialRecordCreate],
          tags=['Financial Records Import'])
async def import_pekaosa(
        file: _fastapi.UploadFile = _fastapi.File(...),
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await financial_record_service.import_pekaosa_csv(db, user, file)


@app.post('/api/grupabps/import_csv', response_model=list[financial_record_schema.FinancialRecordCreate],
          tags=['Financial Records Import'])
async def import_grupabps(
        file: _fastapi.UploadFile = _fastapi.File(...),
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await financial_record_service.import_grupabps_csv(db, user, file)


@app.post('/api/millenium/import_pdf', response_model=list[financial_record_schema.FinancialRecordCreate],
          tags=['Financial Records Import'])
async def import_millenium(
        file: _fastapi.UploadFile = _fastapi.File(...),
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await financial_record_service.import_millenium_pdf(db, user, file)


@app.get('/api/dashboard', response_model=dashboard_schema.Dashboard, tags=['Dashboard'])
async def get_dashboard(
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await dashboard_service.get_dashboard(db, user)


@app.get('/api/dashboard-with-spendings', response_model=dashboard_schema.DashboardWithSpendings, tags=['Dashboard'])
async def get_dashboard_with_spendings(
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
):
    return await dashboard_service.get_dashboard_with_spendings(db, user)


@app.get('/api/categories-dashboard', response_model=dashboard_schema.DashboardCategories, tags=['Dashboard'])
async def get_categories_dashboard(
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
        skip: int = 0,
        limit: int = 100,
        start_date: datetime.date = datetime.date.today().replace(day=1)
):
    return await dashboard_service.get_categories_dashboard(db, user, skip, limit, start_date)


@app.get('/api/budget-dashboard', response_model=dashboard_schema.DashboardBudget, tags=['Dashboard'])
async def get_budget_dashboard(
        user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
        db: _orm.Session = _fastapi.Depends(database_session.database_session),
        skip: int = 0,
        limit: int = 100,
        start_date: datetime.date = datetime.date.today().replace(day=1),
):
    return await dashboard_service.get_budget_dashboard(db, user, skip, limit, start_date)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv("PORT", 80)))
