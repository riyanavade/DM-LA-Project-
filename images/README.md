# Player Portrait Images

Place professional player portrait images here to use them in the app.

Naming convention:
- Use lowercase letters
- Replace spaces with underscores
- Supported extensions: `.jpg`, `.jpeg`, `.png`, `.webp`

Examples:
- `virat_kohli.jpg`
- `rohit_sharma.png`

If you want players to appear in their IPL team jerseys, add team jersey files with this naming pattern:
- `jersey_<team_name>.jpg`
- `jersey_<team_name>.png`

Examples:
- `jersey_mumbai_indians.jpg`
- `jersey_royal_challengers_bangalore.png`

This repo now includes local team jersey files for all 10 IPL teams in `images/`.

The app will automatically use a local team jersey image first, then a remote team jersey/logo image, then a local player portrait image, then the `Photo_URL` field in your uploaded CSV, or a default placeholder.

Currently the repository includes 21 professional player portraits stored locally in this folder. The remaining players still fall back to remote portrait URLs from the app's built-in lookup mapping.

If you have a local photo for MS Dhoni, save it as `ms_dhoni.jpg` in this folder. The app will automatically use it for the player name `MS Dhoni`.

Example filename to add: `ms_dhoni.jpg`
