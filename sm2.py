from datetime import date

from schemas import Review


def update_sm2(review: Review, score: float):
    # score: 0..5 (float albo int)
    score = float(score)
    if score < 3:
        review.repetitions = 0
        review.interval_days = 1
        review.ease_factor = max(1.3, review.ease_factor - 0.2)
    else:
        review.repetitions += 1
        if review.repetitions == 1:
            review.interval_days = 1
        elif review.repetitions == 2:
            review.interval_days = 6
        else:
            review.interval_days = int(round(review.interval_days * review.ease_factor))
        # standardowa aktualizacja EF:
        review.ease_factor += (0.1 - (5 - score) * (0.08 + (5 - score) * 0.02))
        if review.ease_factor < 1.3:
            review.ease_factor = 1.3
    review.created_at = date.today()
    review.score = score
