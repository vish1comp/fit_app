import json
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.models import User, FoodItem, Exercise, Supplement, Subscription
from app.core.security import get_password_hash
from datetime import datetime

# Make sure tables exist
Base.metadata.create_all(bind=engine)


def seed_database():
    db: Session = SessionLocal()
    try:
        print("Seeding database...")

        # 1. Seed Admin User
        admin_email = "admin@fitsphere.ai"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                hashed_password=get_password_hash("password123"),
                name="Admin Administrator",
                age=30,
                gender="male",
                height_cm=180.0,
                weight_kg=80.0,
                activity_level="moderately_active",
                fitness_goal="recomposition",
                is_verified=True,
                is_admin=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

            # Create Pro Subscription for Admin
            sub = Subscription(
                user_id=admin.id,
                plan_type="pro",
                status="active",
                current_period_end=datetime(2030, 1, 1),
            )
            db.add(sub)
            db.commit()
            print("Admin user and pro subscription created!")
        else:
            print("Admin user already exists.")

        # 2. Seed Foods
        foods_data = [
            {"name": "Chicken Breast", "brand": "Generic Raw", "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0, "sugar": 0, "sodium": 74, "serving_size": "100g", "serving_size_g": 100, "category": "protein"},
            {"name": "Eggs", "brand": "Generic Large", "calories": 78, "protein": 6, "carbs": 0.6, "fat": 5, "fiber": 0, "sugar": 0.6, "sodium": 62, "serving_size": "1 Egg (50g)", "serving_size_g": 50, "category": "protein"},
            {"name": "White Rice", "brand": "Generic Cooked", "calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "fiber": 0.4, "sugar": 0.1, "sodium": 1, "serving_size": "100g", "serving_size_g": 100, "category": "carb"},
            {"name": "Paneer", "brand": "Generic Cottage Cheese", "calories": 265, "protein": 18, "carbs": 1.2, "fat": 20.8, "fiber": 0, "sugar": 1.2, "sodium": 18, "serving_size": "100g", "serving_size_g": 100, "category": "protein"},
            {"name": "Rolled Oats", "brand": "Generic Raw", "calories": 389, "protein": 16.9, "carbs": 66.3, "fat": 6.9, "fiber": 10.6, "sugar": 0, "sodium": 2, "serving_size": "100g", "serving_size_g": 100, "category": "carb"},
            {"name": "Banana", "brand": "Generic Raw", "calories": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3, "fiber": 2.6, "sugar": 12.2, "sodium": 1, "serving_size": "1 Medium (118g)", "serving_size_g": 118, "category": "fruit"},
            {"name": "Apple", "brand": "Generic Red", "calories": 52, "protein": 0.3, "carbs": 13.8, "fat": 0.2, "fiber": 2.4, "sugar": 10.4, "sodium": 1, "serving_size": "1 Medium (182g)", "serving_size_g": 182, "category": "fruit"},
            {"name": "Whey Protein", "brand": "Premium Standard", "calories": 120, "protein": 24, "carbs": 3, "fat": 1.5, "fiber": 0, "sugar": 1, "sodium": 50, "serving_size": "1 Scoop (30g)", "serving_size_g": 30, "category": "protein"},
        ]
        for f in foods_data:
            existing = db.query(FoodItem).filter(FoodItem.name == f["name"]).first()
            if not existing:
                food = FoodItem(**f, is_admin_created=True)
                db.add(food)
        db.commit()
        print("Foods database seeded!")

        # 3. Seed Exercises
        exercises_data = [
            # Chest
            {
                "name": "Bench Press", "muscle_group": "chest", "difficulty": "intermediate", "equipment": "barbell",
                "video_url": "https://www.youtube.com/watch?v=rT7DgCr-3ps",
                "instructions": "1. Lie flat on the bench, feet flat on the floor. 2. Grip the barbell slightly wider than shoulder width. 3. Unrack and lower it slowly to mid-chest. 4. Push back up dynamically keeping elbows tucked at 45 degrees.",
                "common_mistakes": "Bouncing bar off chest, flaring elbows out, lifting hips off bench.", "tips": "Squeeze your shoulder blades together before racking."
            },
            {
                "name": "Incline Press", "muscle_group": "chest", "difficulty": "intermediate", "equipment": "dumbbell",
                "video_url": "https://www.youtube.com/watch?v=8iPjxAQs8bc",
                "instructions": "1. Sit on a bench set to a 30-45 degree incline. 2. Lift dumbbells to shoulders. 3. Press weights straight up over your upper chest. 4. Control weight on the way down.",
                "common_mistakes": "Incline set too high (delegates work to shoulders), dropping weights out wide.", "tips": "Focus on driving your biceps towards each other."
            },
            {
                "name": "Push-Ups", "muscle_group": "chest", "difficulty": "beginner", "equipment": "bodyweight",
                "instructions": "1. Place hands shoulder-width on the floor, feet together. 2. Keep body in a straight plank line. 3. Lower chest until it almost touches the floor. 4. Push back up to lock.",
                "common_mistakes": "Sagging hips, head craning forward, elbows flaring.", "tips": "Brace your abs like you are expecting a punch."
            },
            # Back
            {
                "name": "Pull-Ups", "muscle_group": "back", "difficulty": "intermediate", "equipment": "bodyweight",
                "instructions": "1. Hang from a bar with hands wider than shoulder-width, palms facing away. 2. Pull yourself up by driving elbows down until chin clears the bar. 3. Control down to dead hang.",
                "common_mistakes": "Kicking legs (kipping), not going all the way down, using neck to reach bar.", "tips": "Depress shoulder blades before pulling."
            },
            {
                "name": "Deadlift", "muscle_group": "back", "difficulty": "advanced", "equipment": "barbell",
                "instructions": "1. Stand with mid-foot under the bar. 2. Hinge down and grip bar. 3. Flatten back, pull chest up. 4. Push feet through floor and stand up. 5. Reverse hip hinge to lower.",
                "common_mistakes": "Rounding the spine (cat back), bar drifting forward, hyperextending at top.", "tips": "Keep the bar in contact with your shins and thighs throughout."
            },
            {
                "name": "Barbell Rows", "muscle_group": "back", "difficulty": "intermediate", "equipment": "barbell",
                "instructions": "1. Hinge at hips with back flat, parallel to floor. 2. Pull barbell to lower chest/sternum. 3. Squeeze shoulder blades at top. 4. Return to full arm extension.",
                "common_mistakes": "Standing too upright, pulling with momentum (cheating), rounding lower back.", "tips": "Pull with your elbows, not your hands."
            },
            # Shoulders
            {
                "name": "Overhead Press", "muscle_group": "shoulders", "difficulty": "intermediate", "equipment": "barbell",
                "instructions": "1. Stand tall, grip bar at shoulders. 2. Pull chin back slightly. 3. Press bar directly overhead, locking elbows and pushing head forward. 4. Return down controlled.",
                "common_mistakes": "Excessive back arching, not locking out, bar path curving around face.", "tips": "Squeeze glutes and quads to create a rigid base."
            },
            {
                "name": "Lateral Raises", "muscle_group": "shoulders", "difficulty": "beginner", "equipment": "dumbbell",
                "instructions": "1. Hold dumbbells at sides, tilt torso slightly forward. 2. Raise arms out to sides in a wide arc. 3. Lower slowly back to hips.",
                "common_mistakes": "Swinging hips to move weight, raising hands higher than elbows.", "tips": "Imagine pouring water out of two cups at the top."
            },
            # Legs
            {
                "name": "Squats", "muscle_group": "legs", "difficulty": "intermediate", "equipment": "barbell",
                "instructions": "1. Place bar on upper back. 2. Stand feet shoulder-width, toes slightly out. 3. Push hips back and lower until thighs are parallel or deeper. 4. Stand back up powerfully.",
                "common_mistakes": "Knees caving inwards (valgus), heels lifting off floor, rounding low back at bottom.", "tips": "Keep weight centered over mid-foot."
            },
            {
                "name": "Lunges", "muscle_group": "legs", "difficulty": "beginner", "equipment": "dumbbell",
                "instructions": "1. Take a large step forward. 2. Lower hips until back knee almost touches the floor, front thigh parallel. 3. Push off front foot to return.",
                "common_mistakes": "Knee drifting too far forward, stepping in a straight line (tightrope), losing balance.", "tips": "Step out slightly wide for better balance."
            },
            {
                "name": "Leg Press", "muscle_group": "legs", "difficulty": "beginner", "equipment": "machine",
                "instructions": "1. Sit in sled, feet shoulder-width on platform. 2. Lower sled slowly until knees are at 90 degrees. 3. Push back up without locking knees.",
                "common_mistakes": "Locking knees completely, lifting lower back off seat, too shallow ROM.", "tips": "Keep your heels flat against the platform."
            },
            # Arms
            {
                "name": "Biceps Curl", "muscle_group": "arms", "difficulty": "beginner", "equipment": "dumbbell",
                "instructions": "1. Stand holding dumbbells, palms forward. 2. Curl weights up keeping elbows pinned to sides. 3. Squeeze biceps, lower slowly.",
                "common_mistakes": "Elbows drifting forward, swinging hips, not extending arms fully at bottom.", "tips": "Keep wrists straight."
            },
            {
                "name": "Tricep Pushdown", "muscle_group": "arms", "difficulty": "beginner", "equipment": "cable",
                "instructions": "1. Hold bar attached to high cable, elbows pinned to ribs. 2. Push bar down until arms are locked out. 3. Return slowly to 90 degree elbow angle.",
                "common_mistakes": "Elbows flaring out, shoulders hunching over weight, leaning too far forward.", "tips": "Use a rope attachment for better triceps extension."
            },
            # Core
            {
                "name": "Plank", "muscle_group": "core", "difficulty": "beginner", "equipment": "bodyweight",
                "instructions": "1. Place forearms on ground, body in straight line. 2. Squeeze glutes and abs to hold flat torso. 3. Breathe deeply, hold.",
                "common_mistakes": "Hips sagging down, hips piked too high, head dropping down.", "tips": "Pull elbows towards toes to increase intensity."
            },
            {
                "name": "Hanging Leg Raises", "muscle_group": "core", "difficulty": "intermediate", "equipment": "bodyweight",
                "instructions": "1. Hang from pullup bar. 2. Keep legs straight and lift them until parallel to floor. 3. Lower slowly without swinging.",
                "common_mistakes": "Swinging for momentum, dropping legs instantly.", "tips": "Initiate the movement by rolling your pelvis upwards."
            }
        ]
        for ex in exercises_data:
            existing = db.query(Exercise).filter(Exercise.name == ex["name"]).first()
            if not existing:
                exercise = Exercise(**ex)
                db.add(exercise)
        db.commit()
        print("Exercises database seeded!")

        # 4. Seed Supplements
        supp_data = [
            {
                "name": "Whey Protein", "category": "protein",
                "description": "High-quality, fast-digesting milk-derived protein rich in Branched-Chain Amino Acids (BCAAs).",
                "benefits": "Supports muscle growth, speeds muscle tissue recovery, and makes hitting daily protein targets convenient.",
                "side_effects": "Digestive discomfort for individuals with lactose intolerance.",
                "dosage": "1-2 scoops (25-50g) daily, adjusted according to general diet.",
                "timing": "Excellent post-workout or between meals.",
                "warnings": "Individuals with dairy allergies should choose plant-based isolates.",
                "scientific_evidence": "Robust clinical trials consistently show whey increases muscle mass when paired with resistance training.",
                "evidence_rating": "strong",
                "references_json": ["Morton et al., 2018 (British Journal of Sports Medicine)", "Devries & Phillips, 2015 (Journal of Food Science)"]
            },
            {
                "name": "Creatine Monohydrate", "category": "creatine",
                "description": "A naturally occurring compound that helps regenerate Adenosine Triphosphate (ATP), the primary energy source for short-burst actions.",
                "benefits": "Increases muscular power, maximum strength output, muscle cell hydration, and cognitive performance.",
                "side_effects": "Slight initial water retention, mild stomach cramping if taken with insufficient water.",
                "dosage": "3-5g daily. Loading phase (20g/day for 5 days) is optional but not required.",
                "timing": "Take daily at any consistent time (e.g. post-workout with carbs).",
                "warnings": "Ensure high daily water intake (3L+). Consult physician if having pre-existing renal disease.",
                "scientific_evidence": "Hundreds of peer-reviewed studies establish creatine monohydrate as the gold standard for performance enhancement.",
                "evidence_rating": "strong",
                "references_json": ["Buford et al., 2007 (ISSN Position Stand)", "Kreider et al., 2017 (Journal of the International Society of Sports Nutrition)"]
            },
            {
                "name": "Fish Oil", "category": "recovery",
                "description": "Supplement rich in Omega-3 fatty acids: Eicosapentaenoic Acid (EPA) and Docosahexaenoic Acid (DHA).",
                "benefits": "Reduces chronic inflammation, promotes heart health, supports joint lubrication, and improves brain function.",
                "side_effects": "Fishy aftertaste (can be mitigated by freezing capsules), mild blood thinning at high doses.",
                "dosage": "1-2g of combined EPA/DHA daily.",
                "timing": "Take with meals containing fats to maximize absorption.",
                "warnings": "Caution if taking prescription blood thinners or having seafood allergies.",
                "scientific_evidence": "Strong scientific backing for cardiovascular health benefits and reducing joint soreness.",
                "evidence_rating": "strong",
                "references_json": ["Albert et al., 2016 (AHA Circulation)", "Jouris et al., 2011 (Journal of Sports Science & Medicine)"]
            },
            {
                "name": "Caffeine", "category": "pre-workout",
                "description": "Central nervous system stimulant widely consumed to reduce perceived exertion.",
                "benefits": "Enhances alertness, sharpens focus, increases muscular endurance, and boosts metabolic rate.",
                "side_effects": "Jitters, anxiety, increased heart rate, sleep disruption if taken late in the day.",
                "dosage": "3-6mg per kg of bodyweight taken before exercise (~150-300mg).",
                "timing": "Consume 30-45 minutes before a workout.",
                "warnings": "Avoid within 6-8 hours of sleep. Monitor tolerance carefully.",
                "scientific_evidence": "Consistently proven in meta-analyses to improve power output, running speed, and fat oxidation.",
                "evidence_rating": "strong",
                "references_json": ["Grgic et al., 2018 (Journal of the International Society of Sports Nutrition)", "Goldstein et al., 2010 (ISSN Position Stand)"]
            }
        ]
        for s in supp_data:
            existing = db.query(Supplement).filter(Supplement.name == s["name"]).first()
            if not existing:
                supp = Supplement(**s)
                db.add(supp)
        db.commit()
        print("Supplements database seeded!")
        print("All database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
