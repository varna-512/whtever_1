import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [data, setData] = useState(null);
  const [mlData, setMlData] = useState(null);
  const [error, setError] = useState("");

  // ==================================================
  // FETCH DATA FROM FLASK BACKEND
  // ==================================================

  useEffect(() => {
    Promise.all([
      fetch("http://127.0.0.1:5000/api/latest"),
      fetch("http://127.0.0.1:5000/api/prediction"),
      fetch("http://127.0.0.1:5000/api/forecast"),
    ])
      .then(async ([latestResponse, mlResponse, forecastResponse]) => {
        if (
          !latestResponse.ok ||
          !mlResponse.ok ||
          !forecastResponse.ok
        ) {
          throw new Error("Backend request failed");
        }

        const latestData = await latestResponse.json();
        const predictionData = await mlResponse.json();
        const forecastData = await forecastResponse.json();

        return {
          latestData,
          predictionData,
          forecastData,
        };
      })
      .then(
        ({
          latestData,
          predictionData,
          forecastData,
        }) => {
          console.log(
            "HEATWISE FORECAST:",
            forecastData
          );

          setData({
            ...latestData,
            forecast: forecastData,
          });

          setMlData(predictionData);
        }
      )
      .catch((err) => {
        console.error(err);
        setError(
          "Unable to connect to HEATWISE backend."
        );
      });
  }, []);

  // ==================================================
  // BACKEND ERROR
  // ==================================================

  if (error) {
    return (
      <div className="error-screen">
        <div className="error-card">
          <div className="error-icon">!</div>

          <h2>HEATWISE Backend Offline</h2>

          <p>{error}</p>

          <small>
            Make sure Flask is running on port 5000.
          </small>
        </div>
      </div>
    );
  }

  // ==================================================
  // LOADING
  // ==================================================

  if (!data || !mlData) {
    return (
      <div className="loading-screen">
        <div className="loading-card">
          <div className="loading-icon">🔥</div>

          <h2>HEATWISE</h2>

          <p>Loading heat intelligence...</p>
        </div>
      </div>
    );
  }

  // ==================================================
  // BASIC DATA
  // ==================================================

  const riskScore = Number(
    data.final_risk_score || 0
  );

  const temperature = Number(
    data.temperature || 0
  );

  const mortalityRR = Number(
    data.mortality_rr || 1
  );

  const hospitalizationRR = Number(
    data.hospitalization_rr || 1
  );

  const vulnerability = Number(
    data.vulnerability_score || 0
  );

  const riskCategory =
    data.final_risk_category || "LOW";

  // ==================================================
  // MACHINE LEARNING DATA
  // ==================================================

  const mlRisk =
    mlData.predicted_risk ||
    "LOW / MODERATE";

  const mlConfidence = Number(
    mlData.confidence || 0
  );

  const lowProbability = Number(
    mlData.low_moderate_probability || 0
  );

  const highProbability = Number(
    mlData.high_extreme_probability || 0
  );

  // ==================================================
  // FORECAST DATA
  // ==================================================

  const forecast =
    data.forecast?.predictions || [];

  // ==================================================
  // RECOMMENDATION
  // ==================================================

  const getRecommendation = () => {
    if (riskScore >= 70) {
      return {
        title: "Activate Extreme Heat Response",
        description:
          "Issue public heat-health warnings and prioritize vulnerable groups.",
        priority: "URGENT",
      };
    }

    if (riskScore >= 40) {
      return {
        title: "Issue Heat-Health Warning",
        description:
          "Advise vulnerable groups to reduce outdoor exposure and increase monitoring.",
        priority: "HIGH",
      };
    }

    return {
      title: "Continue Routine Monitoring",
      description:
        "Maintain routine monitoring and normal heat-safety awareness.",
      priority: "NORMAL",
    };
  };

  const recommendation =
    getRecommendation();

  // ==================================================
  // RISK CLASS
  // ==================================================

  const getRiskClass = () => {
    if (riskScore >= 70) return "extreme";

    if (riskScore >= 40) return "high";

    return "low";
  };

  const riskClass = getRiskClass();

  // ==================================================
  // DATE FORMAT
  // ==================================================

  const formatDate = (dateString) => {
    if (!dateString) return "—";

    const date = new Date(dateString);

    return date.toLocaleDateString(
      "en-IN",
      {
        day: "2-digit",
        month: "short",
        year: "numeric",
      }
    );
  };

  // ==================================================
  // FORECAST GRAPH
  // ==================================================

  const getForecastValue = (prediction) => {
    if (
      prediction.prediction_class === 1
    ) {
      return 78;
    }

    return 38;
  };

  const graphWidth = 1000;
  const graphHeight = 300;

  const graphPoints = forecast.map(
    (prediction, index) => {
      const x =
        forecast.length === 1
          ? graphWidth / 2
          : (index /
              (forecast.length - 1)) *
            graphWidth;

      const riskValue =
        getForecastValue(prediction);

      const y =
        graphHeight -
        (riskValue / 100) *
          graphHeight;

      return {
        ...prediction,
        x,
        y,
      };
    }
  );

  const graphLine =
    graphPoints.length > 0
      ? graphPoints
          .map(
            (point, index) =>
              `${index === 0 ? "M" : "L"} ${
                point.x
              } ${point.y}`
          )
          .join(" ")
      : "";

  // ==================================================
  // DASHBOARD
  // ==================================================

  return (
    <div className="app">

      {/* ==================================================
          SIDEBAR
      ================================================== */}

      <aside className="sidebar">

        <div className="logo">

          <div className="logo-icon">
            H
          </div>

          <div>
            <h2>HEATWISE</h2>

            <span>
              Heat Intelligence
            </span>
          </div>

        </div>

        <nav>

          <div className="nav-item active">
            <span>◉</span>
            Dashboard
          </div>

          <div className="nav-item">
            <span>▣</span>
            Risk Monitor
          </div>

          <div className="nav-item">
            <span>♥</span>
            Health Impact
          </div>

          <div className="nav-item">
            <span>♙</span>
            Vulnerability
          </div>

          <div className="nav-item">
            <span>⚠</span>
            Alerts
          </div>

        </nav>

        <div className="sidebar-bottom">

          <div className="system-status">
            <span className="status-dot"></span>
            System Operational
          </div>

          <small>
            HEATWISE • Prototype v1.0
          </small>

        </div>

      </aside>


      {/* ==================================================
          MAIN
      ================================================== */}

      <main className="main">

        {/* ==================================================
            HEADER
        ================================================== */}

        <header className="header">

          <div>

            <p className="eyebrow">
              URBAN HEAT INTELLIGENCE
            </p>

            <h1>
              Ahmedabad Heat Risk Dashboard
            </h1>

            <p className="subtitle">
              Integrated environmental, health and
              vulnerability assessment
            </p>

          </div>

          <div className="header-right">

            <div className="location">
              <span>●</span>
              Ahmedabad, Gujarat
            </div>

            <div className="date-box">

              <small>
                ANALYSIS DATE
              </small>

              <strong>
                {formatDate(data.date)}
              </strong>

            </div>

          </div>

        </header>


        {/* ==================================================
            TOP CARDS
        ================================================== */}

        <section className="cards">

          {/* FINAL RISK */}

          <div
            className={`card risk-card ${riskClass}`}
          >

            <div className="card-top">

              <span>
                FINAL HEAT RISK
              </span>

              <span className="card-icon">
                🔥
              </span>

            </div>

            <h2>
              {riskCategory}
            </h2>

            <p>
              Composite risk assessment
            </p>

            <div className="risk-score">

              <strong>
                {riskScore.toFixed(1)}
              </strong>

              <span>
                / 100
              </span>

            </div>

          </div>


          {/* TEMPERATURE */}

          <div className="card">

            <div className="card-top">

              <span>
                TEMPERATURE
              </span>

              <span className="card-icon">
                🌡
              </span>

            </div>

            <h2>
              {temperature.toFixed(1)}°C
            </h2>

            <p>
              Maximum temperature
            </p>

            <div className="mini-stat">

              <span>
                Heat severity
              </span>

              <strong>
                {data.heat_severity}
              </strong>

            </div>

          </div>


          {/* HEALTH */}

          <div className="card">

            <div className="card-top">

              <span>
                HEALTH IMPACT
              </span>

              <span className="card-icon">
                ♥
              </span>

            </div>

            <h2>

              {mortalityRR >= 1.4
                ? "VERY HIGH"
                : mortalityRR >= 1.2
                ? "HIGH"
                : "MODERATE"}

            </h2>

            <p>
              Heat-related health risk
            </p>

            <div className="mini-stat">

              <span>
                Mortality RR
              </span>

              <strong>
                {mortalityRR.toFixed(3)}
              </strong>

            </div>

          </div>


          {/* VULNERABILITY */}

          <div className="card">

            <div className="card-top">

              <span>
                VULNERABILITY
              </span>

              <span className="card-icon">
                ♙
              </span>

            </div>

            <h2>
              {vulnerability.toFixed(1)}
            </h2>

            <p>
              Vulnerability score
            </p>

            <div className="mini-stat">

              <span>
                Population aged 60+
              </span>

              <strong>
                India
              </strong>

            </div>

          </div>

        </section>


        {/* ==================================================
            CONTENT GRID
        ================================================== */}

        <section className="content-grid">

          {/* MAP */}

          <div className="panel map-panel">

            <div className="panel-header">

              <div>

                <p className="panel-label">
                  SPATIAL RISK
                </p>

                <h3>
                  Ahmedabad Risk Map
                </h3>

              </div>

              <button>
                Risk Zones ▾
              </button>

            </div>

            <div className="map-placeholder">

              <div className="map-grid"></div>

              <div
                className={`map-center ${riskClass}`}
              >

                <div className="pulse"></div>

                <span>
                  Ahmedabad
                </span>

              </div>

              <div className="map-label label-1">
                EXTREME
              </div>

              <div className="map-label label-2">
                HIGH
              </div>

              <div className="map-label label-3">
                MODERATE
              </div>

              <div className="map-legend">

                <span>
                  Risk Level
                </span>

                <div>
                  ● Extreme
                </div>

                <div>
                  ● High
                </div>

                <div>
                  ● Moderate
                </div>

              </div>

            </div>

          </div>


          {/* MACHINE LEARNING */}

          <div className="panel ml-panel">

            <div className="panel-header">

              <div>

                <p className="panel-label">
                  MACHINE LEARNING
                </p>

                <h3>
                  Risk Prediction
                </h3>

              </div>

              <span className="ai-badge">
                RANDOM FOREST
              </span>

            </div>

            <div className="prediction">

              <span>
                Predicted Risk
              </span>

              <strong>
                {mlRisk}
              </strong>

              <small>
                Prediction confidence:{" "}
                {mlConfidence}%
              </small>

            </div>

            <div className="probability">

              <div>

                <span>
                  LOW / MODERATE
                </span>

                <strong>
                  {lowProbability}%
                </strong>

              </div>

              <div className="bar">

                <div
                  className="bar-fill low"
                  style={{
                    width:
                      `${lowProbability}%`,
                  }}
                ></div>

              </div>


              <div>

                <span>
                  HIGH / EXTREME
                </span>

                <strong>
                  {highProbability}%
                </strong>

              </div>

              <div className="bar">

                <div
                  className="bar-fill high"
                  style={{
                    width:
                      `${highProbability}%`,
                  }}
                ></div>

              </div>

            </div>

          </div>

        </section>


        {/* ==================================================
            5-DAY FORECAST
        ================================================== */}

        <section
          className="panel"
          style={{
            marginTop: "24px",
            padding: "24px",
          }}
        >

          {/* HEADER */}

          <div
            style={{
              display: "flex",
              justifyContent:
                "space-between",
              alignItems: "flex-start",
              marginBottom: "10px",
            }}
          >

            <div>

              <p className="panel-label">
                PREDICTIVE OUTLOOK
              </p>

              <h3>
                5-Day Heat Risk Forecast
              </h3>

              <p
                style={{
                  marginTop: "6px",
                  fontSize: "12px",
                  opacity: 0.6,
                }}
              >
                Historical walk-forward prototype
                • Next-day risk predictions
              </p>

            </div>

            <span className="ai-badge">
              RANDOM FOREST
            </span>

          </div>


          {/* GRAPH */}

          {forecast.length > 0 ? (

            <div
              style={{
                marginTop: "25px",
                position: "relative",
              }}
            >

              {/* Y AXIS LABELS */}

              <div
                style={{
                  position: "absolute",
                  left: 0,
                  top: 0,
                  bottom: "55px",
                  width: "55px",
                  display: "flex",
                  flexDirection:
                    "column",
                  justifyContent:
                    "space-between",
                  fontSize: "9px",
                  opacity: 0.55,
                  padding:
                    "5px 0",
                }}
              >

                <span>HIGH</span>
                <span>MODERATE</span>
                <span>LOW</span>

              </div>


              {/* SVG GRAPH */}

              <svg
                viewBox={`0 0 ${graphWidth} ${graphHeight}`}
                width="100%"
                height="300"
                preserveAspectRatio="none"
                style={{
                  display: "block",
                  marginLeft: "55px",
                  width:
                    "calc(100% - 55px)",
                  overflow: "visible",
                }}
              >

                {/* BACKGROUND ZONES */}

                <rect
                  x="0"
                  y="0"
                  width={graphWidth}
                  height="100"
                  fill="rgba(190,70,45,0.04)"
                />

                <rect
                  x="0"
                  y="100"
                  width={graphWidth}
                  height="100"
                  fill="rgba(210,145,70,0.04)"
                />

                <rect
                  x="0"
                  y="200"
                  width={graphWidth}
                  height="100"
                  fill="rgba(90,130,90,0.04)"
                />


                {/* GRID LINES */}

                <line
                  x1="0"
                  y1="100"
                  x2={graphWidth}
                  y2="100"
                  stroke="rgba(0,0,0,0.1)"
                  strokeDasharray="5 5"
                />

                <line
                  x1="0"
                  y1="200"
                  x2={graphWidth}
                  y2="200"
                  stroke="rgba(0,0,0,0.1)"
                  strokeDasharray="5 5"
                />

                <line
                  x1="0"
                  y1="299"
                  x2={graphWidth}
                  y2="299"
                  stroke="rgba(0,0,0,0.12)"
                />


                {/* FORECAST LINE */}

                {graphLine && (
                  <path
                    d={graphLine}
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    opacity="0.65"
                  />
                )}


                {/* FORECAST POINTS */}

                {graphPoints.map(
                  (point, index) => {

                    const isHigh =
                      point.prediction_class ===
                      1;

                    return (
                      <g
                        key={
                          point.forecast_date
                        }
                      >

                        {/* OUTER RING */}

                        <circle
                          cx={point.x}
                          cy={point.y}
                          r="12"
                          fill="white"
                          opacity="0.9"
                        />

                        {/* POINT */}

                        <circle
                          cx={point.x}
                          cy={point.y}
                          r="7"
                          fill="white"
                          stroke={
                            isHigh
                              ? "#bd4c3b"
                              : "#d18b52"
                          }
                          strokeWidth="4"
                        />

                        {/* CHECKPOINT NUMBER */}

                        <text
                          x={point.x}
                          y={
                            point.y - 22
                          }
                          textAnchor="middle"
                          fontSize="10"
                          fontWeight="600"
                          fill="currentColor"
                        >
                          {index + 1}
                        </text>

                      </g>
                    );
                  }
                )}

              </svg>


              {/* CHECKPOINT CARDS */}

              <div
                style={{
                  marginLeft: "55px",
                  display: "grid",
                  gridTemplateColumns:
                    `repeat(${forecast.length}, 1fr)`,
                  gap: "8px",
                  marginTop: "10px",
                }}
              >

                {forecast.map(
                  (prediction, index) => {

                    const isHigh =
                      prediction.prediction_class ===
                      1;

                    return (
                      <div
                        key={
                          prediction.forecast_date
                        }
                        style={{
                          textAlign: "center",
                          padding: "10px 5px",
                          borderTop:
                            "1px solid rgba(0,0,0,0.08)",
                        }}
                      >

                        <div
                          style={{
                            fontSize: "8px",
                            letterSpacing:
                              "0.08em",
                            opacity: 0.5,
                            marginBottom:
                              "4px",
                          }}
                        >
                          {index === 0
                            ? "NEXT DAY"
                            : `+${index + 1} DAY`}
                        </div>

                        <strong
                          style={{
                            display: "block",
                            fontSize: "11px",
                            marginBottom:
                              "6px",
                          }}
                        >
                          {formatDate(
                            prediction.forecast_date
                          )}
                        </strong>

                        <span
                          style={{
                            display:
                              "inline-block",
                            fontSize: "9px",
                            fontWeight: "600",
                            padding:
                              "4px 7px",
                            borderRadius:
                              "20px",
                            background:
                              isHigh
                                ? "rgba(189,76,59,0.1)"
                                : "rgba(209,139,82,0.1)",
                            color:
                              isHigh
                                ? "#b64032"
                                : "#c27c45",
                          }}
                        >
                          {prediction.predicted_risk}
                        </span>

                        <small
                          style={{
                            display:
                              "block",
                            marginTop:
                              "5px",
                            fontSize:
                              "9px",
                            opacity: 0.55,
                          }}
                        >
                          {prediction.confidence}%
                          {" "}confidence
                        </small>

                      </div>
                    );
                  }
                )}

              </div>

            </div>

          ) : (

            <div
              style={{
                padding: "50px",
                textAlign: "center",
                opacity: 0.6,
              }}
            >
              Forecast data unavailable.
            </div>

          )}


          {/* FORECAST SUMMARY */}

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(3, 1fr)",
              gap: "12px",
              marginTop: "25px",
              paddingTop: "20px",
              borderTop:
                "1px solid rgba(0,0,0,0.08)",
            }}
          >

            <div
              style={{
                padding: "12px",
                background:
                  "rgba(0,0,0,0.025)",
                borderRadius: "8px",
              }}
            >

              <strong
                style={{
                  display: "block",
                  fontSize: "11px",
                }}
              >
                5-Day Outlook
              </strong>

              <small
                style={{
                  display: "block",
                  marginTop: "4px",
                  fontSize: "9px",
                  opacity: 0.55,
                }}
              >
                Continuous heat-risk projection
              </small>

            </div>


            <div
              style={{
                padding: "12px",
                background:
                  "rgba(0,0,0,0.025)",
                borderRadius: "8px",
              }}
            >

              <strong
                style={{
                  display: "block",
                  fontSize: "11px",
                }}
              >
                ML Powered
              </strong>

              <small
                style={{
                  display: "block",
                  marginTop: "4px",
                  fontSize: "9px",
                  opacity: 0.55,
                }}
              >
                Random Forest predictions
              </small>

            </div>


            <div
              style={{
                padding: "12px",
                background:
                  "rgba(0,0,0,0.025)",
                borderRadius: "8px",
              }}
            >

              <strong
                style={{
                  display: "block",
                  fontSize: "11px",
                }}
              >
                Walk-Forward
              </strong>

              <small
                style={{
                  display: "block",
                  marginTop: "4px",
                  fontSize: "9px",
                  opacity: 0.55,
                }}
              >
                Historical validation prototype
              </small>

            </div>

          </div>

        </section>


        {/* ==================================================
            LOWER GRID
        ================================================== */}

        <section className="lower-grid">


          {/* RISK DRIVERS */}

          <div className="panel">

            <div className="panel-header">

              <div>

                <p className="panel-label">
                  RISK DRIVERS
                </p>

                <h3>
                  Why is the risk high?
                </h3>

              </div>

            </div>


            <div className="drivers">


              {/* TEMPERATURE */}

              <div className="driver">

                <div>

                  <span>
                    Maximum Temperature
                  </span>

                  <small>
                    {temperature.toFixed(1)}°C
                  </small>

                </div>

                <div className="driver-bar">

                  <div
                    style={{
                      width:
                        `${Math.min(
                          (temperature / 50) *
                            100,
                          100
                        )}%`,
                    }}
                  ></div>

                </div>

              </div>


              {/* MORTALITY */}

              <div className="driver">

                <div>

                  <span>
                    Mortality Risk
                  </span>

                  <small>
                    RR {mortalityRR.toFixed(3)}
                  </small>

                </div>

                <div className="driver-bar">

                  <div
                    style={{
                      width:
                        `${Math.min(
                          Math.max(
                            ((mortalityRR - 1) /
                              0.5) *
                              100,
                            0
                          ),
                          100
                        )}%`,
                    }}
                  ></div>

                </div>

              </div>


              {/* HEAT RISK */}

              <div className="driver">

                <div>

                  <span>
                    Heat Risk Score
                  </span>

                  <small>
                    {Number(
                      data.heat_risk_score || 0
                    ).toFixed(1)}
                  </small>

                </div>

                <div className="driver-bar">

                  <div
                    style={{
                      width:
                        `${Math.min(
                          Number(
                            data.heat_risk_score ||
                              0
                          ),
                          100
                        )}%`,
                    }}
                  ></div>

                </div>

              </div>


              {/* HOSPITALIZATION */}

              <div className="driver">

                <div>

                  <span>
                    Hospitalization Risk
                  </span>

                  <small>
                    RR{" "}
                    {hospitalizationRR.toFixed(
                      3
                    )}
                  </small>

                </div>

                <div className="driver-bar">

                  <div
                    style={{
                      width:
                        `${Math.min(
                          Math.max(
                            ((hospitalizationRR -
                              1) /
                              4) *
                              100,
                            0
                          ),
                          100
                        )}%`,
                    }}
                  ></div>

                </div>

              </div>

            </div>

          </div>


          {/* RESPONSE ENGINE */}

          <div className="panel action-panel">

            <div className="panel-header">

              <div>

                <p className="panel-label">
                  RESPONSE ENGINE
                </p>

                <h3>
                  Recommended Action
                </h3>

              </div>

              <span
                className={`priority ${riskClass}`}
              >
                {recommendation.priority}
              </span>

            </div>

            <div className="action-main">

              <div className="action-icon">
                ⚠
              </div>

              <div>

                <h4>
                  {recommendation.title}
                </h4>

                <p>
                  {recommendation.description}
                </p>

              </div>

            </div>

            <div className="action-list">

              <div>
                ✓ Issue heat-health warning
              </div>

              <div>
                ✓ Advise vulnerable groups
                to avoid exposure
              </div>

              <div>
                ✓ Increase monitoring of
                emergency admissions
              </div>

            </div>

          </div>

        </section>


        {/* ==================================================
            FOOTER
        ================================================== */}

        <footer>

          <span>
            HEATWISE • Ahmedabad Prototype
          </span>

          <span>
            Environmental + Health +
            Vulnerability + ML
          </span>

        </footer>

      </main>

    </div>
  );
}

export default App;