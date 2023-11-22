import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_plane_movements(previous_df=None):
    titles = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliet"]
    plane_types = ["A320", "B737", "A380", "B747", "Cessna", "Embraer", "Bombardier"]

    if previous_df is None:
        # Initial DataFrame generation
        num_rows = random.randint(10, len(titles))  # Ensure num_rows does not exceed the length of titles
        df = pd.DataFrame({
            "title": random.sample(titles, num_rows),
            "lat": np.random.uniform(-90, 90, size=num_rows),
            "lon": np.random.uniform(-180, 180, size=num_rows),
            "timestamp": [datetime.now() - timedelta(minutes=random.randint(0, 120)) for _ in range(num_rows)],
            "plane_type": [random.choice(plane_types) for _ in range(num_rows)]
        })
    else:
        # Modify the existing DataFrame
        df = previous_df.copy()
        df['lat'] += np.random.uniform(-0.5, 0.5, size=len(df))
        df['lon'] += np.random.uniform(-0.5, 0.5, size=len(df))
        df['timestamp'] = [datetime.now() - timedelta(minutes=random.randint(0, 120)) for _ in range(len(df))]

    # Simulate add/remove 5% of data
    changes = max(1, int(0.05 * len(df)))
    for _ in range(changes):
        if random.random() < 0.5 and len(set(titles) - set(df['title'])) > 0:  # Add a new row if unused titles are available
            new_row = pd.DataFrame([{
                "title": random.choice(list(set(titles) - set(df['title']))),
                "lat": np.random.uniform(-90, 90),
                "lon": np.random.uniform(-180, 180),
                "timestamp": datetime.now() - timedelta(minutes=random.randint(0, 120)),
                "plane_type": random.choice(plane_types)
            }])
            df = pd.concat([df, new_row], ignore_index=True)
        elif len(df) > 1:  # Remove a row if more than one row exists
            df = df.drop(df.sample().index)

    return df

# Example usage
current_df = generate_plane_movements()  # First run
print(current_df)

next_df = generate_plane_movements(current_df)  # Subsequent run
print(next_df)
