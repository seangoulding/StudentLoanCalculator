from flask import Flask, render_template, request, url_for, flash, redirect

import random
import pandas

app = Flask(__name__)
app.config["SECRET_KEY"] = "your secret key"

@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        balance = int(request.form["bal1"])
        years_left = int(request.form["yr"])
        initial_salary = int(request.form["initsal"])
        salary_boost = request.form["salbooist"]
        investment_interest = request.form["yo"]

        z = salary_boost.split(",")
        h = investment_interest.split(",")

        salary_boost = []
        investment_interest = []

        if int(len(z)) > 1:
            for i in range(int(len(z))):
                salary_boost.append(float(z[i]))

        if int(len(h)) > 1:
            for k in range(int(len(h))):
                investment_interest.append(float(h[k]))

        return analyse(balance=balance,years_left=years_left,initial_salary=initial_salary,salary_boost=salary_boost,investment_interest=investment_interest)
    return render_template("index.html")

def analyse(balance, years_left, initial_salary, salary_boost,investment_interest):
    #Would like to randomly compute if worth paying off student loan

    #Independent variables are: {salary, interest, inflation rate}
    #Dependent variables effected are balance, loan repayment, total repaid, sum paid back, etc.
    #for simplicity, would like to focus on only two values - sum paid back if not paid off AND effective cost of paying off (i.e what 34000 today is in 26 yrs when loan is paid off)

    #INITIALISE VARIABLES ------------------------------------------------------------------------------------------------------------------------------------
    #SHOULDN'T BE EDITED:
    threshold = 27295 #governed by law

    final_salary = []
    final_payback_years = []
    final_sum_from_appreciation_due_to_inflation = []
    final_sum_from_appreciation_due_to_investment = []
    final_sum_actual_spent_to_pay_off_loan = []
    final_money_saved = []
    final_money_saved_investment = []
    final_loan_balance = []

    df = pandas.DataFrame(columns = ["Final Salary","Years to Payback","Appreciation of Lump Sum based on Inflation", "Appreciation of Lump Sum from Investment", "Actual sum spent to pay off Loan", "Money Saved by Paying Early (Considers Inflation)", "Money Saved by Paying Early (Considers Investment)"])

    #CAN BE EDITED:
    window = 5 #defines window to change rates
    x = 100 #number of iterations
    #years_left = 28 #number of years before loan is cancelled
    #balance = 34000 #loan balance
    #initial_salary = 40750

    #salary_boost = [0.01, 0.02, 0.03]
    inflation_rate = [0.097, 0.116, 0.041, 0.015, 0.026, 0.033, 0.036, 0.018, 0.010, 0.024, 0.03, 0.032,0.052, 0.046, -0.005, 0.04,0.043,0.032,0.028,0.030,0.029] #20 yrs of inflation rates 2023-2003
    interest_rate = [0.079,0.069,0.045,0.056,0.054,0.063] #interest rates for student loans every march since i've been at uni (2018)
    #investment_interest = [0.02, 0.03, 0.04, 0.05, 0.06] #prediction for how much could gain if not paid to loan.

    #CODE-------------------------------------------------------------------------------------------------------------------------------------------------------


    for iterations in range(x):

        #Reset variables for next iteration
        break_bool = 0
        sum_paid = [0]
        salary = [initial_salary]
        sum_inflation = [balance] 
        sum_investment = [balance]
        loan_balance = [balance]
        year = 0

        for i in range(50): #iteration range greater than 30 so allows code to run when == 30. Range can be anything greater than 30. 50 selected as arbitrary number. Code will always stop before then.
            
            if break_bool == 1:
                final_salary.append(salary[-1])
                final_payback_years.append(len(sum_inflation)-1)
                final_sum_from_appreciation_due_to_inflation.append(sum_inflation[-1])
                final_sum_from_appreciation_due_to_investment.append(sum_investment[-1])
                final_sum_actual_spent_to_pay_off_loan.append(sum(sum_paid))
                final_loan_balance.append(loan_balance[-1])

                #Difference between amount paid to SLC less inflated / invested value of lump sum to pay off the loan. +ve number indicates beneficial to pay off the loan, -ve indicates not beneficial.
                final_money_saved.append(final_sum_actual_spent_to_pay_off_loan[-1] - final_sum_from_appreciation_due_to_inflation[-1])
                final_money_saved_investment.append(final_sum_actual_spent_to_pay_off_loan[-1] - final_sum_from_appreciation_due_to_investment[-1])

                break

            #Randomly select salary boost, inflation, and interest for window size
            selected_boost = random.choice(salary_boost)
            selected_inflation = random.choice(inflation_rate)
            selected_interest = random.choice(interest_rate)
            selected_investment = random.choice(investment_interest)

            #Iterate across window sized number of years, applying randomly selected salary boost, inflation, and interest values.
            for n in range(window):

                #apply yearly salary boost
                salary.append(salary[-1]*(1+selected_boost))

                #apply yearly loan increase
                loan_balance.append(loan_balance[-1]*(1+selected_interest))

                #pay part of loan balance in accordance with salary

                #if sum paid will not pay off remaining loan balance
                if loan_balance[-1] > 0.09*(salary[-1] - threshold) and salary[-1] > threshold:
                    sum_paid.append(0.09*(salary[-1]-threshold))

                    #update loan balance:
                    loan_balance[-1] = loan_balance[-1] - sum_paid[-1]

                #if sum paid will pay off remaining loan balance
                elif loan_balance[-1] > 0 and loan_balance[-1] < 0.09*(salary[-1] - threshold) and salary[-1] > threshold:
                    sum_paid.append(loan_balance[-1])

                    #update loan balance:
                    loan_balance[-1] = 0
                
                sum_inflation.append(sum_inflation[-1]*(1+selected_inflation))
                sum_investment.append(sum_investment[-1]*(1+selected_investment))

                year = year + 1

                if loan_balance[-1] == 0:
                    break_bool = 1
                    break

                elif year == years_left:
                    break_bool = 1
                    break


    #REPRESENTATION OF EACH OUTPUT

    #new_balance_inflation: value of money used to pay off loan today if increases inline with inflation
    #new_balance_interest: actual cost of paying off loan

    df["Final Salary"] = final_salary
    df["Years to Payback"] = final_payback_years
    df["Appreciation of Lump Sum based on Inflation"] = final_sum_from_appreciation_due_to_inflation
    df["Appreciation of Lump Sum from Investment"] = final_sum_from_appreciation_due_to_investment
    df["Actual sum spent to pay off Loan"] = final_sum_actual_spent_to_pay_off_loan
    df["Money Saved by Paying Early (Considers Inflation)"] = final_money_saved
    df["Money Saved by Paying Early (Considers Investment)"] = final_money_saved_investment
    df["Loan balance"] = final_loan_balance

    saved_investment = df["Money Saved by Paying Early (Considers Investment)"].sum()
    saved_inflation = df["Money Saved by Paying Early (Considers Inflation)"].sum()

    if saved_investment > 0 and saved_inflation > 0:
        answer = "should pay it off early"
    elif saved_investment < 0 and saved_inflation > 0:
        answer = "would save more by investing lump sum"
    elif saved_investment > 0 and saved_inflation < 0:
        answer = "shouldn't be printing as this never happens!"
    else:
        answer = "should not pay it off early"

    #df.to_csv("ouput.csv")

    return answer


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000, threaded=True)