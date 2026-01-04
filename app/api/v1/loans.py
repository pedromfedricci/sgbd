from fastapi import APIRouter, status

from app.api.dependencies import loan_service
from app.schemas.loan import LoanCreate, LoanResponse
from app.services.loan import LoanService

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(loan: LoanCreate, loans: LoanService = loan_service()):
    return await loans.create(user_id=loan.user_id, book_id=loan.book_id)


@router.get("/users/{user_id}", response_model=list[LoanResponse])
async def list_loans_by_user(user_id: int, loans: LoanService = loan_service()):
    return await loans.list_by_user(user_id)


@router.get("/active", response_model=list[LoanResponse])
async def list_active_loans(
    offset: int = 0, limit: int = 50, loans: LoanService = loan_service()
):
    return await loans.list_active(offset=offset, limit=limit)


@router.get("/overdue", response_model=list[LoanResponse])
async def list_overdue_loans(
    offset: int = 0, limit: int = 50, loans: LoanService = loan_service()
):
    return await loans.list_overdue(offset=offset, limit=limit)


@router.post("/{loan_id}/return", response_model=LoanResponse)
async def return_loan(loan_id: int, loans: LoanService = loan_service()):
    return await loans.fulfill(loan_id)
