This page is a description of what will happen with regards to the thesis. Purpose: to stay on track :)

# Can machine learning surrogate models accurately approximate computationally expensive stochastic financial pricing models while significantly reducing computational cost?


As part of the writing process we will address the following questions or research "avenues"
1. What is the pricing problem 
2. How is this problem solved with ML
	- Make reference to decision tree 
3. Is Heston pricing actually computationally expensive
4. Can the traditional method already be accelerated 
5. Why use a surrogate model 
6. What previous research has already been done 
7. What should my reference/ground truth be? 
8. How should i generate my data 
9. What should the ML model learn 
10. Which models should I compare
11. How do i decide whether the surrogate is good 
12. How much data do i need
13. What happens when the problem becomes harder
14. Is ML worth it? 
15. Reserach question answers
16. Discussion 


Structure

Heston Model: Created in 3 formats
- SciPy implementation utilizing CPU
- SciPy implementation utilizing GPU 
- QuantLib 
Comparison of each model 
- Measured through absolute error
Validation Tests
1. Ensuring all models reproduce same result 
2. Basic - no arbitrage bound
3. Price should decrease with strike 
4. Price behaviour with spot
5. 