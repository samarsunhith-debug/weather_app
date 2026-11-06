# Project 05 - How I protect the API key

My OpenWeather key is stored only in a local `.env` file, which is listed in
`.gitignore` so it is never committed or uploaded. The code reads it with
`os.getenv("OPENWEATHER_KEY")` (loaded through python-dotenv), so the key never
appears in the source code. The repository contains only `.env.example`, a
template with the placeholder `your_key_here`. I also made sure error messages
never print the request URL, because the URL contains the key, and I checked
with `git status` that `.env` is not tracked.
