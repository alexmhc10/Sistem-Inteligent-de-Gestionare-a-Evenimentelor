from lightfm import LightFM
from lightfm.datasets import fetch_movielens

print("Fetching data…")
data = fetch_movielens(min_rating=4.0)
print("Num users:", data['train'].shape[0], "Num items:", data['train'].shape[1])

model = LightFM(loss='warp', no_components=16, random_state=42)

print("Training…")
model.fit(data['train'], epochs=10, num_threads=4, verbose=True)

print("✓ LightFM ran without errors.")