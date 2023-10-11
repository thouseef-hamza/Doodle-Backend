from django.test import TestCase

# Create your tests here.
for i in range(1,100):
        # otp = random.randint(1000, 9999)
        # user = User.objects.create(
        #     institute_name=fake.first_name(),
        #     email=fake.email(),
        #     phone_number=fake.phone_number(),
        #     otp=otp,
        #     unique_code=next(admin_unique_code),
        #     max_otp_try=settings.MAX_OTP_TRY,
        #     is_active=False,
        #     is_institute=True,
        # )
        # user.set_password(generate_random_password())
        # user.save(update_fields=["password"])
        
        import uuid

        print(str(uuid.uuid3()))

