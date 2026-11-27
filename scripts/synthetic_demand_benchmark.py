"""Reproducible synthetic demand benchmark; not evidence of real restaurant performance."""
import csv
import json
import math
import random
from datetime import date, timedelta
from pathlib import Path

def run(seed=42, days=365):
    rng = random.Random(seed)
    rows = []
    start = date(2025, 1, 1)
    for i in range(days):
        day = start + timedelta(days=i)
        for hour in range(11, 23):
            promo = int(rng.random() < .15)
            peak = math.exp(-((hour-20)/2.2)**2)
            mean = (3 + 12*peak)*(1.35 if day.weekday() >= 4 else 1)*(1+.25*promo)*(1+.12*math.sin(i*2*math.pi/365))
            units = max(0, round(rng.gauss(mean, math.sqrt(mean))))
            rows.append(dict(date=day.isoformat(), weekday=day.weekday(), hour=hour, promotion=promo, units=units))
    cutoff = int(days*.8)*12
    train, test = rows[:cutoff], rows[cutoff:]
    groups = {}
    for r in train:
        key = (r['weekday'], r['hour'], r['promotion'])
        groups.setdefault(key, []).append(r['units'])
    baseline = sum(r['units'] for r in train)/len(train)
    errors = []
    baseline_errors = []
    for r in test:
        values = groups.get((r['weekday'], r['hour'], r['promotion']), [baseline])
        prediction = sum(values)/len(values)
        errors.append(prediction-r['units'])
        baseline_errors.append(baseline-r['units'])
    def metrics(e):
        return dict(mae=sum(map(abs,e))/len(e), rmse=math.sqrt(sum(x*x for x in e)/len(e)))
    return rows, dict(source='synthetic', seed=seed, train_rows=len(train), test_rows=len(test), model='historical conditional mean', metrics=metrics(errors), baseline=metrics(baseline_errors), limitation='Synthetic holdout only; not validated on real sales.')

if __name__ == '__main__':
    rows, report = run()
    out = Path('synthetic_benchmark')
    out.mkdir(exist_ok=True)
    with (out/'demand.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (out/'metrics.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
