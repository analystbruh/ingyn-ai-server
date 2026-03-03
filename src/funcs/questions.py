q1 = """Hey 👋 I’m Ingyn.I’m really glad you’re here.
Before we build your workouts, I want to understand what matters to you. That’s how this works best.
Ready to get started?
"""

q2 = """Amazing.
What’s your main goal right now?
    - Lose fat
    - Build muscle
    - Get stronger
    - Feel healthier & consistent
"""

q3 = """Love that.
How many days per week can you realistically train?

No pressure — just your real schedule.
"""
q4 = """That’s perfect.
One more thing — what usually throws you off track?
    - Busy days
    - Low motivation
    - Not knowing what to do
    - I start strong then fade
"""
q5 = """Here’s what I’m hearing:
    - You want to {ans1}
    - You can train {ans2} days
    - Your biggest challenge is {ans3}
That’s more than enough to build something strong.
When would you like to start? (reply with date in
month/day/year format like 2/14/2026)
"""

q6 = """Perfect.
I’ll guide you day by day — workouts, videos, meals, and check-ins.
You won’t have to guess.
We build this together.
"""

questions = {
    q1: {
        'qid': 1,
        'nextq': q2
    },
    q2: {
        'qid': 2,
        'nextq': q3
    },
    q3: {
        'qid': 3,
        'nextq': q4
    },
    q4: {
        'qid': 4,
        'nextq': q5
    },
    q5: {
        'qid': 5,
        'nextq': q6
    }
}
