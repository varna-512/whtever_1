import math

# Published Ahmedabad mortality anchor
anchor_temperature = 46.8
excess_mortality = 43.1

# Assumed minimum mortality temperature
MMT = 28.0

# Convert excess mortality to relative risk
RR_anchor = 1 + (excess_mortality / 100)

# Calibrate beta
beta = math.log(RR_anchor) / (anchor_temperature - MMT)

print("MORTALITY CALIBRATION")
print("---------------------")
print(f"Anchor temperature : {anchor_temperature} °C")
print(f"Excess mortality   : {excess_mortality}%")
print(f"Relative risk      : {RR_anchor:.3f}")
print(f"MMT                : {MMT} °C")
print(f"Calibrated beta    : {beta:.5f}")

# Check that the equation reproduces the anchor
RR_check = math.exp(beta * max(0, anchor_temperature - MMT))

print(f"RR check            : {RR_check:.3f}")