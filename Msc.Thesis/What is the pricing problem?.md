
1. What is the Heston Model 
	1. Why stochastic volatility 
	2. What do each of the parameters mean 
	3. What assumptions does Heston make 
2. What am I pricing or aiming to price
	1. European call options 
	2. What is the difference between this and anything else
3. What are the inputs and outputs 
4. Other models and why not use them? 


a: This thesis investigates the problem of efficient options pricing. One selection in the stock market is to deal with financial derivatives. Financial derivatives are financial instruments that are linked to a specific financial risks traded on the market. This enables parties to trade specific risks such as interest rates, currencies and etc. (https://www.imf.org/external/np/sta/fd/ 4/9/26). 

The way these contracts work is where there is an agreement between two parties, where the value fluctuates based on the price of one or more underlying assets. Traders can purchase these agreements and utilize them to hedge risk. Contract values depend on changes in the prices of the underlying asset, which is the primary instrument. There are different types of derivatives, as they are based on a wide variety of underlying assets and have many users. Within this, there are two classes of derivative products. Locks and options 
- Locks are products that bind the parties from the outset to agreed upon terms over the life of the contract.
	- futures, forwards and swaps 
	- eg. company 
- Options offer the holder the right to buy and sell an asset at a specific price on or before the options expiry date.
	- 
- With options, we have two different options. 
	- Call 
	- Put 
- Within these options, we have two styles 
	- European and American
In an option-pricing problem, the objective would be to determine the present value of a financial derivative given the characteristics of the following: 
- the contract
- current market conditions 
- parameters of the chosen pricing model. 

In this case we focus on European-style options. There are a variety of different option styles (nasdaq.com, 4th sept 2026)
- European options are contracts that be exercised at expiration. 
- American style: option holder can exercise the option at any time from purchase until the expiration date 

As we are using a European option pricing style. The payoff maturity would be the following:
- max()


--------------------------------------------------------------
Starting off with a bang, financial derivatives are contracts whose value is derived from the value of another asset, such as a stock, bond, commodity and interest rate or market index. Common examples of this include futures and options. Options have a particular importance as they give the holders a right, but not an obligation, to buy or sell an underlying asset under predefined conditions. 

Within options, the holder has two choices they can make. Firstly, they can call. This gives the holder the right to buy an asset at a specified strike price, while a put option gives the holder the right to sell an asset at a specified strike price. The value of an option depends on factors such as the current price of the underlying asset, the strike price, the time remaining until maturity, the interest rate and the volatility of the underlying asset. 

Options can also differ according to their exercise style. A european option can only be exercised at its maturity date, whereas an american option can be exercised at any time, up to and including maturity. Our primary focus on this project is going to be on European options. This is because they provide a relatively controlled setting in which the pricing problem can be studied clearly. The option pricing problem is to determine what this uncertain payoff should be worth today. 

In order to solve this, a mathematical model is required for the evolution of the underlying asset. One of the simplest and most widely known models is the Black-Scholes model, which assumes that volatility remains constant. As we understand it, volatility changes over time and the observed option markets often display volatility. A model that does address this is the heston model, which addresses this limitation by allowing variance of the underlying asset to evolve stochastically. 

