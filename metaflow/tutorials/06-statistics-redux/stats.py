# 1. Rewrite stats.py correctly
cat <<'EOF' > stats.py
import os
import csv
from metaflow import FlowSpec, step, IncludeFile

def script_path(filename):
    return os.path.join(os.path.dirname(__file__), filename)

class MovieStatsFlow(FlowSpec):
    movie_data = IncludeFile(
        'movie_data',
        help='The path to a movie metadata file.',
        default=script_path('../02-statistics/movies.csv'),
    )

    @step
    def start(self):
        lines = [line for line in self.movie_data.splitlines() if line]
        self.data = list(csv.DictReader(lines))
        self.genres = list({
            genre for row in self.data
            for genre in row['genres'].split('|')
        })
        self.next(self.compute_stats, foreach='genres')

    @step
    def compute_stats(self):
        self.genre = self.input
        genre_data = [
            row for row in self.data 
            if self.genre in row['genres'].split('|')
        ]
        scores = sorted([int(row['gross']) for row in genre_data])
        n = len(scores)
        if n > 0:
            self.quartiles = [
                scores[0 if n < 2 else round(n * 0.25)],
                scores[0 if n < 2 else round(n * 0.5)],
                scores[0 if n < 2 else round(n * 0.75)],
            ]
        else:
            self.quartiles = [0, 0, 0]
        self.count = len(genre_data)
        self.next(self.join)

    @step
    def join(self, inputs):
        self.genre_stats = {
            inp.genre.lower(): (inp.count, inp.quartiles)
            for inp in inputs
        }
        self.next(self.end)

    @step
    def end(self):
        print("Flow finished successfully.")

if __name__ == '__main__':
    MovieStatsFlow()
EOF

# 2. Run the code to verify
python stats.py run