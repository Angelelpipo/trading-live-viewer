from pathlib import Path
from urllib.request import Request, urlopen

SOURCE_URL = "https://at.adobe.com/nQ15Afxnu2pZicjx"
OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(parents=True, exist_ok=True)

request = Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
with urlopen(request, timeout=120) as response:
    code = response.read().decode("utf-8-sig")

code = code.replace(
    'indicator("ELPIPO GOD AMD LADDER MASTER v17.9 — REAL ENTRY PNL CALENDAR + SMART DEFAULTS"',
    'indicator("ELPIPO GOD AMD LADDER MASTER v17.9.1 — FIXED 2:1 RISK:REWARD"'
)
code = code.replace("ELPIPO v17.9 ", "ELPIPO v17.9.1 ")

old_settings = '''calendarEntryTouchBufferATR = input.float(0.02, "Entry Touch Tolerance ATR", minval=0.0, maxval=0.50, step=0.01, group=gCalendar)
calendarStopMode = input.string("Opposite Ladder Level", "Calendar Stop Loss Mode", options=["Opposite Ladder Level", "Entry ATR Buffer"], group=gCalendar)
calendarStopBufferATR = input.float(0.05, "Stop Loss Extra Buffer ATR", minval=0.0, maxval=2.0, step=0.01, group=gCalendar)
calendarEntryATRStop = input.float(0.35, "Entry ATR Stop Distance", minval=0.05, maxval=5.0, step=0.05, group=gCalendar)'''
new_settings = '''calendarEntryTouchBufferATR = input.float(0.02, "Entry Touch Tolerance ATR", minval=0.0, maxval=0.50, step=0.01, group=gCalendar)
calendarRiskPerReward = input.float(2.0, "Risk Per 1 Reward — Fixed Default 2:1", minval=1.0, maxval=5.0, step=0.25, group=gCalendar)'''
if old_settings not in code:
    raise RuntimeError("Calendar risk settings block not found")
code = code.replace(old_settings, new_settings)

old_stop = '''calendarEntryTolerance = atr * calendarEntryTouchBufferATR
calendarStopBuffer = atr * calendarStopBufferATR
calendarATRStopDistance = atr * calendarEntryATRStop

// Build the real stop price for the current Brecha entry.
float calendarSignalStop = na
if brechaLiveSide == 1 and not na(brechaEntryLevel)
    if calendarStopMode == "Opposite Ladder Level"
        if brechaEntryText == "+3"
            calendarSignalStop := lvlP2 - calendarStopBuffer
        else if brechaEntryText == "+2"
            calendarSignalStop := lvlP1 - calendarStopBuffer
        else if brechaEntryText == "+1"
            calendarSignalStop := lvlZ - calendarStopBuffer
        else if brechaEntryText == "0"
            calendarSignalStop := lvlM1 - calendarStopBuffer
        else if brechaEntryText == "-1"
            calendarSignalStop := lvlM2 - calendarStopBuffer
        else if brechaEntryText == "-2"
            calendarSignalStop := lvlM3 - calendarStopBuffer
        else
            calendarSignalStop := brechaEntryLevel - nz(ladStep, calendarATRStopDistance) - calendarStopBuffer
    else
        calendarSignalStop := brechaEntryLevel - calendarATRStopDistance
else if brechaLiveSide == -1 and not na(brechaEntryLevel)
    if calendarStopMode == "Opposite Ladder Level"
        if brechaEntryText == "-3"
            calendarSignalStop := lvlM2 + calendarStopBuffer
        else if brechaEntryText == "-2"
            calendarSignalStop := lvlM1 + calendarStopBuffer
        else if brechaEntryText == "-1"
            calendarSignalStop := lvlZ + calendarStopBuffer
        else if brechaEntryText == "0"
            calendarSignalStop := lvlP1 + calendarStopBuffer
        else if brechaEntryText == "+1"
            calendarSignalStop := lvlP2 + calendarStopBuffer
        else if brechaEntryText == "+2"
            calendarSignalStop := lvlP3 + calendarStopBuffer
        else
            calendarSignalStop := brechaEntryLevel + nz(ladStep, calendarATRStopDistance) + calendarStopBuffer
    else
        calendarSignalStop := brechaEntryLevel + calendarATRStopDistance

calendarSignalRisk = not na(calendarSignalStop) and not na(brechaEntryLevel) ? math.abs(brechaEntryLevel - calendarSignalStop) : na
calendarSignalReward = not na(brechaTargetLevel) and not na(brechaEntryLevel) ? math.abs(brechaTargetLevel - brechaEntryLevel) : na
calendarSignalRR = not na(calendarSignalRisk) and calendarSignalRisk > 0 and not na(calendarSignalReward) ? calendarSignalReward / calendarSignalRisk : na'''
new_stop = '''calendarEntryTolerance = atr * calendarEntryTouchBufferATR

// FIXED RISK:REWARD MODEL.
// Reward = distance from Entry to TP.
// Risk = Reward × 2 by default.
// BUY stop sits below Entry. SELL stop sits above Entry.
calendarSignalReward = not na(brechaTargetLevel) and not na(brechaEntryLevel) ? math.abs(brechaTargetLevel - brechaEntryLevel) : na
calendarSignalRisk = not na(calendarSignalReward) ? calendarSignalReward * calendarRiskPerReward : na
float calendarSignalStop = na
if brechaLiveSide == 1 and not na(brechaEntryLevel) and not na(calendarSignalRisk)
    calendarSignalStop := brechaEntryLevel - calendarSignalRisk
else if brechaLiveSide == -1 and not na(brechaEntryLevel) and not na(calendarSignalRisk)
    calendarSignalStop := brechaEntryLevel + calendarSignalRisk
calendarSignalRR = not na(calendarSignalRisk) and calendarSignalRisk > 0 and not na(calendarSignalReward) ? calendarSignalReward / calendarSignalRisk : na'''
if old_stop not in code:
    raise RuntimeError("Calendar stop model block not found")
code = code.replace(old_stop, new_stop)

code = code.replace(
    'rrText = "R:R  1:" + str.tostring(minimumRR, "#.##")',
    'rrText = "RISK:REWARD  " + str.tostring(calendarRiskPerReward, "#.##") + ":1 · WIN +" + str.tostring(1.0 / calendarRiskPerReward, "#.##") + "R · LOSS -1R"'
)
code = code.replace(
    'calendarLegend = "★ FULL · C CUSTOM · GREEN WIN · RED LOSS · GRAY NO ENTRY/WAIT · BLUE ACTIVE · ORANGE SAME BAR"',
    'calendarLegend = "RISK:REWARD " + str.tostring(calendarRiskPerReward, "#.##") + ":1 · WIN +" + str.tostring(1.0 / calendarRiskPerReward, "#.##") + "R · LOSS -1R · GREEN WIN · RED LOSS · ORANGE SAME BAR"'
)

required = ["calendarRiskPerReward", "calendarSignalReward * calendarRiskPerReward", "RISK:REWARD"]
missing = [item for item in required if item not in code]
if missing:
    raise RuntimeError(f"Missing final tokens: {missing}")
if code.count("(") != code.count(")") or code.count("[") != code.count("]"):
    raise RuntimeError("Delimiter validation failed")

pine = OUT / "ELPIPO_GOD_AMD_LADDER_MASTER_v17_9_1_FIXED_2_TO_1_RISK_REWARD.pine"
txt = OUT / "ELPIPO_GOD_AMD_LADDER_MASTER_v17_9_1_FIXED_2_TO_1_RISK_REWARD.txt"
pine.write_text(code, encoding="utf-8")
txt.write_text(code, encoding="utf-8")
print(f"Generated {pine.name} and {txt.name}; {len(code.splitlines())} lines")
