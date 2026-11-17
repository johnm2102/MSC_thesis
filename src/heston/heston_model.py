#libraries
from pathlib import Path 
from time import perf_counter
import json 

import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 
import QuantLib as ql 
from scipy.stats import qmc

#Experiment configuration 
SEED = 42 
N_SAMPLES = 100 
N_STRIKE_CURVES = 5 

K_FIXED = 1.0 
DIVIDEND_YIELD = 0.0 

VALUATION_DATE = ql.Date(2, ql.January, 2026)
DAY_COUNT = ql.Actual365Fixed()

INTEGRATION_ORDERS = (32,64,128)

CONVERGENCE_TOL = 1e-5
BOUND_TOL = 1e-8
SHAPE_TOL = 1e-6

OUTPUT = Path("src/experiments/0_reference_validation")
OUTPUT.mkdir(parents=True, exist_ok=True)

ql.Settings.instance().evaluationDate = VALUATION_DATE

#Heston Pricing Model 
def heston_quantlib_prices(
        S0,
        K,
        T,
        r,
        v0,
        kappa,
        theta,
        sigma,
        rho,
        q=DIVIDEND_YIELD, 
        integration_order=128, 
        option_type = ql.Option.Call
):
    ql.Settings.instance().evaluationDate = VALUATION_DATE

    maturity_date = (
        VALUATION_DATE
        + max(1,int(round(float(T) * 365)))
    )

    spot = ql.QuoteHandle(
        ql.SimpleQuote(float(S0))
    )

    risk_free_curve = ql.YieldTermStructureHandle(
            ql.FlatForward(
                VALUATION_DATE,
                float(r),
                DAY_COUNT
        )
    )

    dividend_curve = ql.YieldTermStructureHandle(
            ql.FlatForward(
                VALUATION_DATE,
                float(q),
                DAY_COUNT
            )
    )

    process = ql.HestonProcess(
        risk_free_curve,
        dividend_curve,
        spot,
        float(v0),
        float(kappa),
        float(theta),
        float(sigma),
        float(rho)
    )

    heston_model = ql.HestonModel(process)

    engine = ql.AnalyticHestonEngine(heston_model, int(integration_order))

    payoff = ql.PlainVanillaPayoff(
        option_type,
        float(K)
    )

    exercise = ql.EuropeanExercise(maturity_date)

    option = ql.VanillaOption(
        payoff,
        exercise
    )

    option.setPricingEngine(engine)

    return float(option.NPV())


def sample_liu_params(n, seed):
    columns = [
        "m", 
        "T", 
        "r", 
        "rho", 
        "kappa", 
        "theta", 
        "sigma", 
        "v0"
    ]
    lower = [0.6, 0.1, 0.0, -0.95, 0.0, 0.0, 0.05]
    upper = [1.4, 1.4, 0.1, 0.0, 2.0, 0.5, 0.5, 0.5]
    
    sampler = qmc.LatinHypercube(d=len(columns), seed=seed)
    values = qmc.scale(sampler.random(n), lower, upper)
    frame = pd.DataFrame(values, columns=columns)

    frame["K"] = K_FIXED
    frame["S0"] = frame["m"] * frame["K"]
    frame["q"] = DIVIDEND_YIELD 
    frame["T_effective"] = np.maximum(
        1,
        np.round(frame["T"]* 365).astype(int)
    )/365.0

    frame["feller_satisfied"] = (
        2 * frame["kappa"] * frame["theta"] >= frame["sigma"] ** 2 
    )
    return frame 


def run_reference_checks(frame):
    records = []
    for i, row in enumerate(
        frame.itertuples(index=False),
        start=1
    ):
        result = row._asdict()
        for order in INTEGRATION_ORDERS:
            start = perf_counter()
            try:
                value = heston_quantlib_prices(
                    S0= row.S0,
                    K = row.K, 
                    T = row.T, 
                    r = row.r, 
                    v0 = row.v0, 
                    kappa = row.kappa, 
                    theta = row.theta, 
                    sigma = row.sigma, 
                    rho = row.rho, 
                    q = row.q, 
                    integration_order= order 
                )

                error = ""
            except Exception as exc: 
                value = np.nan
                error = f"{type(exc).__name__}:{exc}"
            result[f"price_{order}"] = value 
            result[f"second_{order}"] = (perf_counter() - start)
            result[f"error_{order}"] = error 
        p32 = result["price_32"]
        p64 = result["price_64"]
        p128 = result["price_128"]

        result["difference_32_64"] = abs(p32 - p64)
        result["difference_64_128"] = abs(p64 - p128)
        result["converged"] = bool(
            np.isfinite(result["difference_64_128"])
            and result["difference_64_128"]
            <= CONVERGENCE_TOL
        )

        #European call bounds
        T = row.T_effective
        lower = max(
            0.0, 
            row.S0 * np.exp(-row.q * T) - row.K * np.exp(-row.r * T)
        )
        upper = row.S0 * np.exp(-row.q * T)

        result["lower_bound"] = lower 
        result["upper_bound"] = upper 

        result["valid_price"] = bool(
            np.isfinite(p128)
            and lower - BOUND_TOL
            <= p128
            <= upper + BOUND_TOL
        )
        records.append(result)
        if i % 20 == 0 or i == len(frame):
            print(
                f"Validation {i}/{len(frame)}"
                "parameter combinations"
            )
    return pd.DataFrame(records)


def run_shape_checks(frame):
    records = []
    for i, row in enumerate(
        frame.head(N_STRIKE_CURVES).itertuples(
            index = False 
        ), 
        start = 1
    ):
        moneyness = np.linspace(0.7, 1.3, 13)
        strikes = np.sort(row.S0/moneyness)
        try:
            calls = np.array([
                heston_quantlib_prices(
                    S0 = row.S0,
                    K = K, 
                    T = row.T, 
                    r = row.R, 
                    v0 = row.v0, 
                    kappa=row.kappa, 
                    theta=row.theta, 
                    sigma=row.sigma, 
                    rho=row.rho,
                    q=row.q,
                    integration_order=128
                )
                for K in strikes
            ])

            monotone = bool(
                np.all(
                    np.diff(calls) <= SHAPE_TOL
                )
            )

            slopes = (
                np.diff(calls)/np.diff(strikes)
            )
            convex = bool(
                np.all(
                    np.diff(slopes) >= -SHAPE_TOL
                )
            )

            call = heston_quantlib_prices(
                row.S0,
                row.K, 
                row.T,
                row.v0,
                row.kappa,
                row.theta, 
                row.sigma, 
                row.rho,
                q=row.q,
                integration_order=128   
            )

            put = heston_quantlib_prices(
                row.S0,
                row.K, 
                row.T,
                row.v0,
                row.kappa,
                row.theta, 
                row.sigma, 
                row.rho,
                q=row.q,
                integration_order=128, 
                option_type=ql.Option.Put   
            )

            parity_rhs = (
                row.S0 * np.exp(
                    -row.q * row.T_effective
                )
                - row.K * np.exp(
                    -row.r * row.T_effective
                )
            )

            parity_error = abs(
                (call - put) - parity_rhs
            )

            error = ""

        except Exception as exc:
            monotone = False 
            convex = False 
            parity_error = np.nan 
            error = f"{type(exc).__name__}:{exc}"
        
        records.append({
            "curve_id": i, 
            "strike_monotonicity": monotone, 
            "strike_convexity_ok": convex,
            "put_call_parity_abs_error": parity_error, 
            "error": error
        })
    return pd.DataFrame(records)



def main():
    parameters = sample_liu_params(
        N_SAMPLES, 
        SEED
    )

    results = run_reference_checks(parameters)
    shape = run_shape_checks(parameters)
    results.to_csv(
        OUTPUT/"reference_validation.csv",
        index=False 
    )
    shape.to_csv(
        OUTPUT/"strike_shape_checks.csv", 
        index=False
    )
    valid_diffs = (
        results["difference_64_128"].dropna()
    )
    summary = {
        "n_parameters_combinations": int(len(results)),
        "valid_prices": int(results["valid_price"].sum()),
        "failed_128_order_prices": int(results["prices_128"].isna().sum()),
        "converged_64_to_128": int(results["converged"].sum()),
        "feller_satisfied": int(results["feller_satisfied"].sum()),
        "mean_abs_difference_64_128": (
            float(valid_diffs.mean())
            if len(valid_diffs) else None 
        ),
        "max_abs_difference_64_128":(
            float(valid_diffs.max())
            if len(valid_diffs) else None 
        ),
        "mean_seconds_per_price_order_128": float(results["seconds_128"].mean()),
        "strike_monotonicity_passed": int(shape["strike_monotonicity_ok"].sum()),
        "strike_convexity_passed": int(shape["strike_monotonicity_ok"].sum()),
        "max_out_call_parity_error":(
            float(shape["put_call_parity_abs_error"].max())
            if shape["put_call_parity_abs_error"].notna().any()
            else None
        ),
        "independent_solver_comparison_completed": False
    }
    (OUTPUT/"summary.json").write_text(
        json.dumps(summary, indent=2)
    )

    errors = (results["difference_64_128"].dropna())

    plt.figure(figsize=(10,10))
    plt.hist(errors,bins=20)
    plt.axvline(
        CONVERGENCE_TOL,
        color="red",
        linestyle="--",
        label = "Tolerance"
    )

    plt.xlabel(
        "Absolute price difference: "
        "64 vs 128 integration points"
    )
    plt.ylabel("Count")
    plt.title("Heston Numerical convergence check")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        OUTPUT / "convergence_histogram.png", dpi=180
    )

    plt.close()

    print("\n REFERENCE VALIDATION SUMMARY")
    for name, value in summary.items():
        print(f"{name}:{value}")

    print(f"\nResults saved in: {OUTPUT.resolve()}")
    print(
        "NOTE: Numerical stability does not establish"
        "independent agreement with Liu COS method"
    )


if __name__ == "__main__":
    main() 

