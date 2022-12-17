from db.services import (
    create_database,
    database_session,
    user_service as user_service,
    category_service as category_service,
)

from db.schemas import (
    user_schema as user_schema,
    category_schema as category_schema,
)

import jwt as _jwt
import fastapi as _fastapi
import fastapi.security as _security
import sqlalchemy.orm as _orm


app = _fastapi.FastAPI()

create_database.create_database()

@app.get('/')
async def root():
    return {'Status': 'OK'}


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

    await user_service.create_user(db, user)

    return await user_service.create_token(user)


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


@app.get('/api/users/me', response_model=user_schema.User, tags=['User'])
async def get_user(
    user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
):
    return user


@app.get('/api/categories', response_model=list[category_schema.Category], tags=['Category'])
async def get_categories(
    user: user_schema.User = _fastapi.Depends(user_service.get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: _orm.Session = _fastapi.Depends(database_session.database_session)
):
    return await category_service.get_categories(db, user, skip, limit)


@app.post('/api/categories', response_model=category_schema.Category ,tags=['Category'])
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

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
