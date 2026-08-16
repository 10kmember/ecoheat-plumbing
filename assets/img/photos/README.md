# Photographs

Drop EcoHeat's own photographs in this folder using the exact filenames below,
then run `python3 build.py` from the repository root. The build picks them up
automatically and swaps the branded "photograph to follow" panel for the real
image, keeping the alt text that is already written for it.

**No stock photography.** Every slot below is for EcoHeat's own work, van, team
or premises. Generic library images of anonymous engineers actively hurt a local
trades site — visitors are looking for evidence that *you* did the work.

## Filenames the build looks for

| Filename | Where it appears | Shot needed |
| --- | --- | --- |
| `heat-pump-hero.jpg` | Home page, renewables section | An engineer commissioning an air source heat pump |
| `heat-pump-survey.jpg` | Grants page | Carrying out a heat loss survey indoors — clipboard, laser measure, radiator |
| `team.jpg` | About page | The engineers, outdoors, in branded workwear |
| `van.jpg` | About page | The branded van at a customer's property |
| `boiler-installation.jpg` | Boiler installation service page | A finished install: tidy pipework, filter, labelled controls |
| `boiler-servicing-and-repairs.jpg` | Servicing service page | Flue gas analyser in use on a serviced boiler |
| `air-source-heat-pumps.jpg` | Heat pump service page | An installed outdoor unit on a Somerset property |
| `plumbing-and-bathrooms.jpg` | Plumbing service page | A completed bathroom |
| `emergency-plumbing.jpg` | Emergency service page | A repair in progress — leak, isolated pipework |
| `annual-service-plans.jpg` | Service plans page | An engineer at a customer's door or completing a service record |

## Case study photographs

These are before/after pairs referenced from `src/content.py`:

| Filename | Shot needed |
| --- | --- |
| `heat-pump-edingworth-before.jpg` | The old oil boiler and pipework, before removal |
| `heat-pump-edingworth-after.jpg` | The heat pump unit installed on the exterior wall |
| `combi-swap-weston-before.jpg` | The original back boiler behind the fireplace |
| `combi-swap-weston-after.jpg` | The new combi, filter and pipework |
| `bathroom-burnham-before.jpg` | The dated bathroom before strip-out |
| `bathroom-burnham-after.jpg` | The finished walk-in shower room |

## Shooting and preparation notes

- **Before shots matter more than you think.** Take one on every job, from the
  same position you will take the after shot. It costs ten seconds and it is
  the single most persuasive thing on a trades website.
- **Landscape, 4:3 or 16:9.** Portrait phone shots crop awkwardly in the grid.
- **Resize to 1600px on the long edge** and save as JPEG at quality 80 before
  committing. A 4MB phone photo will make the page slower than every competitor
  in Somerset.
- **Permission.** Get the customer's agreement in writing before photographing
  inside their home and publishing it. The privacy policy relies on consent as
  the lawful basis for this, and consent can be withdrawn — if it is, delete the
  file and re-run the build.
- **Nothing identifying.** No house numbers, number plates, post, or anything
  through a window that locates the property.

## Adding a new case study

Add an entry to `CASE_STUDIES` in `src/content.py` with its `photos` list, then
drop the files here and rebuild. Missing files are not an error — the panel
appears instead, so the page is never broken by an image that has not arrived.
