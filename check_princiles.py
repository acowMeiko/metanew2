import json

p = r"d:\experiment\code\metanew2\output\local_inference_with_accuracy.json"
data = json.load(open(p, "r", encoding="utf-8"))

def acc(items):
    if not items: return (0,0,0)
    c = sum(1 for x in items if x.get("is_correct"))
    return (len(items), c, c/len(items))

t = [x for x in data if x.get("has_principles") is True]
f = [x for x in data if x.get("has_principles") is False]
print("has_principles=True :", acc(t))
print("has_principles=False:", acc(f))