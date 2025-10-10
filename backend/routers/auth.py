from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db, User, Ambassador
from ..schemas import OTPRequest, OTPVerify, Token, User as UserSchema, AmbassadorCreate
from ..auth import send_otp, verify_otp, create_access_token, get_current_user
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/request-otp")
async def request_otp(request: OTPRequest, db: Session = Depends(get_db)):
    """Request OTP for phone number"""
    # Check if user exists, if not create them
    user = db.query(User).filter(User.phone_number == request.phone_number).first()
    if not user:
        user = User(phone_number=request.phone_number)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Send OTP
    otp = send_otp(request.phone_number)
    
    return {"message": "OTP sent successfully", "phone_number": request.phone_number}

@router.post("/verify-otp", response_model=Token)
async def verify_otp_endpoint(request: OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP and return access token"""
    if not verify_otp(request.phone_number, request.otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Get or create user
    user = db.query(User).filter(User.phone_number == request.phone_number).first()
    if not user:
        user = User(phone_number=request.phone_number, is_verified=True)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.is_verified = True
        db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.phone_number}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register-ambassador")
async def register_ambassador(
    ambassador_data: AmbassadorCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register as an ambassador"""
    # Check if user is already an ambassador
    existing_ambassador = db.query(Ambassador).filter(Ambassador.user_id == current_user.id).first()
    if existing_ambassador:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an ambassador"
        )
    
    # Create ambassador
    ambassador = Ambassador(
        user_id=current_user.id,
        full_name=ambassador_data.full_name
    )
    db.add(ambassador)
    db.commit()
    db.refresh(ambassador)
    
    return {"message": "Ambassador registered successfully", "ambassador_id": ambassador.id}

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user