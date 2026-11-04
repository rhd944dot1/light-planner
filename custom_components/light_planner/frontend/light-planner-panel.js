// Light Planner panel. Plain web component without a build step.

const I18N = {
  en: {
    title: "Light Planner",
    flows: "Flows",
    new_flow: "New flow",
    default_name: "New flow",
    unnamed: "Unnamed",
    empty_title: "Create your first flow",
    empty_body: "A flow has a name and a timeline: each row is a target like a light, device, area, label or scene, and each bar is a time window for it.",
    showing: "Showing {day}",
    row_one: "{count} row",
    row_other: "{count} rows",
    enabled: "Enabled",
    name: "Flow name",
    name_placeholder: "Evening lights",
    remove: "Remove {name}",
    no_options: "Nothing available",
    add_row: "Add row",
    row_section: "Row",
    left_out: "{count} left out",
    row_target: "Row target",
    timeline: "Timeline",
    timeline_hint: "Drag a bar to move it, drag its edge to change the time, click an empty spot to add a time window.",
    timeline_hint_touch: "Tap a bar to select it. Then drag its arrows to change the time, or the bar itself to move it. Tapping an empty spot clears the selection, after that it adds a time window.",
    own_row_hint: "A row naming a light wins wherever it has a bar. Outside that bar, the light follows the rows reaching it through a device, area, floor or label.",
    no_rows: "Add a light, device, area, label or scene to start.",
    light_one: "{count} light",
    light_other: "{count} lights",
    not_this_day: "Doesn't run on {day}",
    selected: "Time window: {who}",
    select_bar: "Select a row or a bar to edit it.",
    remove_bar: "Remove time window",
    starts: "Starts",
    ends: "Ends",
    time: "Time",
    not_before: "Not before",
    offset: "Offset (min)",
    sun_below: "Sun drops below (°)",
    at_start: "At start",
    on_arrival: "On arrival",
    at_end: "At end",
    only_when: "Only when",
    person: "Person",
    respect_manual: "Don't touch manually changed lights",
    manual_hint: "Counts every change that doesn't come from Light Planner, also from other automations.",
    manual_hours: "Changed in the last (hours), or while the flow runs",
    manual_now: "Left alone right now",
    manual_since: "{name}, changed at {time}",
    manual_clear: "Follow the flow again: {name}",
    look: "Look",
    scene_activates: "This scene is activated when the time window starts.",
    plain_words: "In plain words",
    icons: "What the icons mean",
    icons_when: "When",
    icons_what: "What",
    icons_after: "Afterwards",
    icons_condition: "Condition",
    icons_arrival: "Arriving home",
    icons_row: "Row",
    save: "Save",
    saved: "Saved",
    unsaved: "Unsaved changes",
    apply_now: "Apply now",
    apply_now_title: "Applies what this flow schedules for this moment, whatever its condition says.",
    applied: "Applied",
    delete: "Delete",
    delete_confirm: "Really delete?",
    discard: "Discard changes",
    simulation: "Simulation",
    day: "Day",
    at: "at",
    now: "Now",
    no_lights: "No lights in any flow yet.",
    unchanged: "Unchanged",
    off: "Off",
    also_activated: "Also activated: {scenes}",
    scene_bar: "Scene",
    "type.light": "Light",
    "type.device": "Device",
    "type.area": "Area",
    "type.floor": "Floor",
    "type.label": "Label",
    "type.scene": "Scene",
    "type.several": "Several targets",
    "start.time": "Time",
    "start.sunset": "Sunset",
    "start.sunrise": "Sunrise",
    "start.sun_elevation": "Sun elevation",
    "end.time": "Time",
    "end.sunset": "Sunset",
    "end.sunrise": "Sunrise",
    "at_start.turn_on": "Turn on",
    "at_start.adjust": "Only adjust if on",
    "on_arrival.apply": "Apply",
    "on_arrival.nothing": "Do nothing",
    "at_end.turn_off": "Turn off",
    "at_end.restore": "Restore previous state",
    "at_end.nothing": "Do nothing",
    "condition.always": "Presence doesn't matter",
    "condition.anyone_home": "Anyone is home",
    "condition.everyone_home": "Everyone is home",
    "condition.nobody_home": "Nobody is home",
    "condition.person": "A specific person is home",
    "look_mode.keep": "Keep color",
    "look_mode.white": "White",
    "look_mode.color": "Color",
    "look_mode.off": "Off",
    "look_mode.unchanged": "Leave alone",
    set_brightness: "Set brightness",
    brightness: "Brightness",
    temperature: "Temperature",
    color: "Color",
    "preset.warm": "Warm white",
    "preset.neutral": "Neutral white",
    "preset.cool": "Cool white",
    "preset.red": "Red",
    "preset.orange": "Orange",
    "preset.pink": "Pink",
    "preset.purple": "Purple",
    "preset.blue": "Blue",
    "preset.green": "Green",
    "hue.red": "red",
    "hue.orange": "orange",
    "hue.yellow": "yellow",
    "hue.green": "green",
    "hue.cyan": "cyan",
    "hue.blue": "blue",
    "hue.purple": "purple",
    "hue.pink": "pink",
    "white.warm": "warm white",
    "white.neutral": "neutral white",
    "white.cool": "cool white",
    "days.all": "Every day",
    "days.weekdays": "Weekdays",
    "days.weekend": "Weekends",
    "s.pick_day": "Pick at least one day to see what this flow does.",
    "s.no_bars": "Add a time window to see what this flow does.",
    "s.intro": "{days}{condition}:",
    "s.cond.always": "",
    "s.cond.anyone_home": ", but only when someone is home",
    "s.cond.everyone_home": ", but only when everyone is home",
    "s.cond.nobody_home": ", but only when nobody is home",
    "s.cond.person": ", but only when {person} is home",
    "s.sun.sunset": "sunset",
    "s.sun.sunrise": "sunrise",
    "s.after": "{minutes} min after {sun}",
    "s.before": "{minutes} min before {sun}",
    "s.elevation": "the sun dropping below {deg}°",
    "s.not_before": "{start} (not before {time})",
    "s.area": "the area {name}",
    "s.floor": "the floor {name}",
    "s.label": "the label {name}",
    "s.without": "{names} without {excluded}",
    "s.bar_on": "{who}: {look} from {start} until {end}",
    "s.bar_adjust": "{who}: {look} if already on, from {start} until {end}",
    "s.bar_keep": "{who}: stays as it is if on, from {start} until {end}",
    "s.bar_off": "{who}: off from {start} until {end}",
    "s.bar_unchanged": "{who}: left alone from {start} until {end}",
    "s.bar_scene": "{who}: activated from {start} until {end}",
    "s.then_off": ", then off",
    "s.then_restore": ", then back to how it was",
    "s.arrival_apply": "If you arrive home during this time, whatever is scheduled at that moment is applied right away.",
    "s.arrival_nothing": "Arriving home during this time changes nothing.",
    "s.manual": "Lights changed by hand or by anything else in the last {hours} hours, or while this flow runs, stay as they are until the end action.",
    "s.look_on": "on",
    "s.look_on_percent": "on at {percent}%",
    "s.look_named": "{look}",
    "s.look_named_percent": "{look} at {percent}%",
  },
  de: {
    title: "Light Planner",
    flows: "Flows",
    new_flow: "Neuer Flow",
    default_name: "Neuer Flow",
    unnamed: "Ohne Namen",
    empty_title: "Erstelle deinen ersten Flow",
    empty_body: "Ein Flow hat einen Namen und eine Zeitleiste: Jede Zeile ist ein Ziel wie ein Licht, Gerät, Bereich, Label oder eine Szene, und jeder Balken ist ein Zeitfenster dafür.",
    showing: "Anzeige für {day}",
    row_one: "{count} Zeile",
    row_other: "{count} Zeilen",
    enabled: "Aktiv",
    name: "Name des Flows",
    name_placeholder: "Abendlicht",
    remove: "{name} entfernen",
    no_options: "Nichts verfügbar",
    add_row: "Zeile hinzufügen",
    row_section: "Zeile",
    left_out: "{count} ausgenommen",
    row_target: "Ziel der Zeile",
    timeline: "Zeitleiste",
    timeline_hint: "Ziehe einen Balken zum Verschieben, ziehe seine Kante zum Ändern der Zeit, klicke auf eine freie Stelle für ein neues Zeitfenster.",
    timeline_hint_touch: "Tippe auf einen Balken zum Auswählen. Dann ziehst du die Pfeile zum Ändern der Zeit oder den Balken zum Verschieben. Tippen auf eine freie Stelle hebt die Auswahl auf, danach legt es ein neues Zeitfenster an.",
    own_row_hint: "Eine Zeile, die ein Licht direkt nennt, gewinnt überall dort, wo sie einen Balken hat. Außerhalb davon folgt das Licht den Zeilen, die es über ein Gerät, einen Bereich, eine Etage oder ein Label erreichen.",
    no_rows: "Füge ein Licht, Gerät, einen Bereich, ein Label oder eine Szene hinzu.",
    light_one: "{count} Licht",
    light_other: "{count} Lichter",
    not_this_day: "Läuft nicht am {day}",
    selected: "Zeitfenster: {who}",
    select_bar: "Wähle eine Zeile oder einen Balken zum Bearbeiten aus.",
    remove_bar: "Zeitfenster entfernen",
    starts: "Start",
    ends: "Ende",
    time: "Uhrzeit",
    not_before: "Nicht vor",
    offset: "Versatz (Min.)",
    sun_below: "Sonne sinkt unter (°)",
    at_start: "Zum Start",
    on_arrival: "Beim Heimkommen",
    at_end: "Zum Ende",
    only_when: "Nur wenn",
    person: "Person",
    respect_manual: "Manuell geänderte Lichter nicht anfassen",
    manual_hint: "Zählt jede Änderung, die nicht von Light Planner kommt, auch von anderen Automationen.",
    manual_hours: "Geändert in den letzten (Stunden) oder während der Flow läuft",
    manual_now: "Gerade ausgelassen",
    manual_since: "{name}, geändert um {time}",
    manual_clear: "Wieder dem Flow folgen: {name}",
    look: "Stimmung",
    scene_activates: "Diese Szene wird aktiviert, wenn das Zeitfenster beginnt.",
    plain_words: "In einfachen Worten",
    icons: "Was die Symbole bedeuten",
    icons_when: "Wann",
    icons_what: "Was",
    icons_after: "Danach",
    icons_condition: "Bedingung",
    icons_arrival: "Heimkommen",
    icons_row: "Zeile",
    save: "Speichern",
    saved: "Gespeichert",
    unsaved: "Nicht gespeicherte Änderungen",
    apply_now: "Jetzt anwenden",
    apply_now_title: "Setzt, was dieser Flow für diesen Moment vorsieht, egal was seine Bedingung sagt.",
    applied: "Angewendet",
    delete: "Löschen",
    delete_confirm: "Wirklich löschen?",
    discard: "Änderungen verwerfen",
    simulation: "Simulation",
    day: "Tag",
    at: "um",
    now: "Jetzt",
    no_lights: "Noch keine Lichter in einem Flow.",
    unchanged: "Unverändert",
    off: "Aus",
    also_activated: "Außerdem aktiviert: {scenes}",
    scene_bar: "Szene",
    "type.light": "Licht",
    "type.device": "Gerät",
    "type.area": "Bereich",
    "type.floor": "Etage",
    "type.label": "Label",
    "type.scene": "Szene",
    "type.several": "Mehrere Ziele",
    "start.time": "Uhrzeit",
    "start.sunset": "Sonnenuntergang",
    "start.sunrise": "Sonnenaufgang",
    "start.sun_elevation": "Sonnenhöhe",
    "end.time": "Uhrzeit",
    "end.sunset": "Sonnenuntergang",
    "end.sunrise": "Sonnenaufgang",
    "at_start.turn_on": "Einschalten",
    "at_start.adjust": "Nur anpassen, wenn an",
    "on_arrival.apply": "Anwenden",
    "on_arrival.nothing": "Nichts tun",
    "at_end.turn_off": "Ausschalten",
    "at_end.restore": "Vorherigen Zustand herstellen",
    "at_end.nothing": "Nichts tun",
    "condition.always": "Anwesenheit egal",
    "condition.anyone_home": "Jemand ist zu Hause",
    "condition.everyone_home": "Alle sind zu Hause",
    "condition.nobody_home": "Niemand ist zu Hause",
    "condition.person": "Eine bestimmte Person ist zu Hause",
    "look_mode.keep": "Farbe beibehalten",
    "look_mode.white": "Weiß",
    "look_mode.color": "Farbe",
    "look_mode.off": "Aus",
    "look_mode.unchanged": "Nicht anfassen",
    set_brightness: "Helligkeit setzen",
    brightness: "Helligkeit",
    temperature: "Farbtemperatur",
    color: "Farbe",
    "preset.warm": "Warmweiß",
    "preset.neutral": "Neutralweiß",
    "preset.cool": "Kaltweiß",
    "preset.red": "Rot",
    "preset.orange": "Orange",
    "preset.pink": "Pink",
    "preset.purple": "Lila",
    "preset.blue": "Blau",
    "preset.green": "Grün",
    "hue.red": "rot",
    "hue.orange": "orange",
    "hue.yellow": "gelb",
    "hue.green": "grün",
    "hue.cyan": "cyan",
    "hue.blue": "blau",
    "hue.purple": "lila",
    "hue.pink": "pink",
    "white.warm": "warmweiß",
    "white.neutral": "neutralweiß",
    "white.cool": "kaltweiß",
    "days.all": "Jeden Tag",
    "days.weekdays": "Montag bis Freitag",
    "days.weekend": "Am Wochenende",
    "s.pick_day": "Wähle mindestens einen Tag, um zu sehen, was dieser Flow tut.",
    "s.no_bars": "Füge ein Zeitfenster hinzu, um zu sehen, was dieser Flow tut.",
    "s.intro": "{days}{condition}:",
    "s.cond.always": "",
    "s.cond.anyone_home": ", aber nur wenn jemand zu Hause ist",
    "s.cond.everyone_home": ", aber nur wenn alle zu Hause sind",
    "s.cond.nobody_home": ", aber nur wenn niemand zu Hause ist",
    "s.cond.person": ", aber nur wenn {person} zu Hause ist",
    "s.sun.sunset": "Sonnenuntergang",
    "s.sun.sunrise": "Sonnenaufgang",
    "s.after": "{minutes} Min. nach {sun}",
    "s.before": "{minutes} Min. vor {sun}",
    "s.elevation": "Sonnenhöhe unter {deg}°",
    "s.not_before": "{start} (nicht vor {time})",
    "s.area": "Bereich {name}",
    "s.floor": "Etage {name}",
    "s.label": "Label {name}",
    "s.without": "{names} ohne {excluded}",
    "s.bar_on": "{who}: {look} von {start} bis {end}",
    "s.bar_adjust": "{who}: {look}, wenn schon an, von {start} bis {end}",
    "s.bar_keep": "{who}: bleibt wie es ist, wenn an, von {start} bis {end}",
    "s.bar_off": "{who}: aus von {start} bis {end}",
    "s.bar_unchanged": "{who}: wird nicht angefasst von {start} bis {end}",
    "s.bar_scene": "{who}: aktiviert von {start} bis {end}",
    "s.then_off": ", danach aus",
    "s.then_restore": ", danach wie vorher",
    "s.arrival_apply": "Kommst du in dieser Zeit heim, wird sofort angewendet, was in dem Moment geplant ist.",
    "s.arrival_nothing": "Heimkommen ändert in dieser Zeit nichts.",
    "s.manual": "Lichter, die in den letzten {hours} Stunden oder während dieser Flow läuft von Hand oder anderweitig geändert wurden, bleiben bis zur Endaktion, wie sie sind.",
    "s.look_on": "an",
    "s.look_on_percent": "an mit {percent} %",
    "s.look_named": "{look}",
    "s.look_named_percent": "{look} mit {percent} %",
    "err.Pick a start time.": "Wähle eine Startzeit.",
    "err.Enter a sun elevation.": "Gib eine Sonnenhöhe ein.",
    "err.Pick an end time.": "Wähle eine Endzeit.",
    "err.Start and end can't be the same time.": "Start und Ende dürfen nicht gleich sein.",
    "err.Give this flow a name.": "Gib diesem Flow einen Namen.",
    "err.Pick at least one day.": "Wähle mindestens einen Tag.",
    "err.Pick a person.": "Wähle eine Person.",
    "err.Each target can only be in one row.": "Jedes Ziel darf nur in einer Zeile stehen.",
    "err.Pick a target for every row.": "Wähle für jede Zeile ein Ziel.",
    "err.Add at least one time window.": "Füge mindestens ein Zeitfenster hinzu.",
    "err.Time windows in one row can't overlap.": "Zeitfenster einer Zeile dürfen sich nicht überschneiden.",
    "err.Pick a time.": "Wähle eine Uhrzeit.",
  },
};

const PRESETS = [
  ["preset.warm", { mode: "white", kelvin: 2200 }],
  ["preset.neutral", { mode: "white", kelvin: 4000 }],
  ["preset.cool", { mode: "white", kelvin: 6000 }],
  ["preset.red", { mode: "color", rgb: [255, 30, 20] }],
  ["preset.orange", { mode: "color", rgb: [255, 120, 20] }],
  ["preset.pink", { mode: "color", rgb: [255, 60, 150] }],
  ["preset.purple", { mode: "color", rgb: [140, 70, 255] }],
  ["preset.blue", { mode: "color", rgb: [30, 90, 255] }],
  ["preset.green", { mode: "color", rgb: [40, 200, 80] }],
];

const HANDLE = 36;

const STYLE = `
:host { display: block; min-height: 100%; background: var(--primary-background-color); color: var(--primary-text-color);
  font-family: var(--paper-font-body1_-_font-family, var(--ha-font-family-body, sans-serif)); font-size: 14px; }
* { box-sizing: border-box; }
[hidden] { display: none !important; }
header { display: flex; align-items: center; gap: 8px; height: var(--header-height, 56px); padding: 0 16px;
  background: var(--app-header-background-color, var(--primary-color)); color: var(--app-header-text-color, #fff); font-size: 20px; }
header button { background: none; border: 0; color: inherit; padding: 8px; font-size: 20px; line-height: 1; min-height: 0; }
main { max-width: 960px; margin: 0 auto; padding: 16px; }
.card { background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 12px; padding: 16px; margin-bottom: 16px; }
.head { display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }
.muted { color: var(--secondary-text-color); font-size: 12px; }
.sec { color: var(--secondary-text-color); font-size: 12px; font-weight: 500; margin: 18px 0 8px; }
button, select, input { font: inherit; color: var(--primary-text-color); }
button { background: transparent; border: 1px solid var(--divider-color); border-radius: 8px; padding: 6px 12px; min-height: 36px; cursor: pointer; }
button:hover { background: var(--secondary-background-color); }
button:focus-visible, select:focus-visible, input:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 1px; }
button.primary { background: var(--primary-color); border-color: var(--primary-color); color: var(--text-primary-color, #fff); }
button.primary:hover { filter: brightness(1.08); background: var(--primary-color); }
button.danger { color: var(--error-color); }
select, input[type=text], input[type=time], input[type=number] { width: 100%; min-height: 36px; padding: 4px 8px; border-radius: 8px;
  border: 1px solid var(--divider-color); background: var(--secondary-background-color); }
input[type=range] { width: 100%; accent-color: var(--primary-color); }
input[type=checkbox] { accent-color: var(--primary-color); width: 18px; height: 18px; margin: 0; }
label.fld { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--secondary-text-color); min-width: 0; }
label.check { display: inline-flex; align-items: center; gap: 8px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
.scroll { overflow-x: auto; }
.lines { min-width: 760px; }
.line { display: grid; grid-template-columns: 170px minmax(0, 1fr); border-top: 1px solid var(--divider-color); }
.line.axis { border-top: 0; }
.line-name { position: sticky; left: 0; z-index: 4; background: var(--card-background-color); display: flex; align-items: center; gap: 6px;
  padding: 4px 6px 4px 2px; font-size: 13px; font-weight: 500; line-height: 1.25; min-width: 0; overflow-wrap: break-word; }
.line-name ha-icon { color: var(--secondary-text-color); flex: none; }
.line-name small { display: block; font-weight: 400; font-size: 11px; color: var(--secondary-text-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.line-name .clamp { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; hyphens: auto; }
.line-name > span { min-width: 0; }
.line-name { cursor: pointer; }
.line-name.sel { box-shadow: inset 2px 0 0 var(--primary-color); }
.add-row ha-selector, .detail ha-selector { display: block; }
.line-name button { border: 0; padding: 0 4px; min-height: 24px; margin-left: auto; font-size: 15px; line-height: 1; color: var(--secondary-text-color); }
.grid-track { position: relative; background-image: linear-gradient(to right, var(--divider-color) 1px, transparent 1px); background-size: calc(100% / 12) 100%; }
.track { height: 50px; cursor: copy; overflow: hidden; }
.axis .grid-track { height: 42px; background: none; }
.tick { position: absolute; bottom: 2px; font-size: 11px; color: var(--secondary-text-color); transform: translateX(-50%); font-variant-numeric: tabular-nums; }
.tick.first { transform: none; }
.sunmark { position: absolute; top: 0; font-size: 11px; color: var(--warning-color, #e08a00); display: flex; align-items: center; gap: 2px; transform: translateX(-50%); white-space: nowrap; --mdc-icon-size: 15px; }
.sunline { position: absolute; top: 0; bottom: 0; width: 0; border-left: 1px dashed var(--warning-color, #e08a00); pointer-events: none; }
.simline { position: absolute; top: 0; bottom: 0; width: 0; border-left: 2px solid var(--error-color); pointer-events: none; z-index: 3; }
.tbar { position: absolute; top: 8px; bottom: 8px; border-radius: 6px; display: flex; align-items: center; gap: 4px; padding: 0 5px; font-size: 11px;
  white-space: nowrap; overflow: hidden; cursor: grab; touch-action: pan-x pan-y; user-select: none; z-index: 2; box-shadow: inset 0 0 0 1px rgba(0, 0, 0, .18); --mdc-icon-size: 15px; }
.tbar:active { cursor: grabbing; }
.tbar .txt { overflow: hidden; text-overflow: ellipsis; min-width: 0; }
.tbar .spacer { flex: 1; }
.tbar.sel { box-shadow: inset 0 0 0 2px var(--primary-text-color); touch-action: none; }
.tbar:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 1px; }
.tbar.dim { opacity: .45; }
.tbar.wrapping { border-top-right-radius: 0; border-bottom-right-radius: 0; }
.tbar.wrapped { border-top-left-radius: 0; border-bottom-left-radius: 0; }
.tbar.wrapping .grip.r, .tbar.wrapped .grip.l { display: none; }
.paint-off { background: repeating-linear-gradient(135deg, var(--secondary-background-color), var(--secondary-background-color) 5px, var(--divider-color) 5px, var(--divider-color) 10px); color: var(--primary-text-color); }
.paint-unchanged { background: var(--card-background-color); color: var(--secondary-text-color); box-shadow: inset 0 0 0 1px var(--secondary-text-color); }
.paint-scene { background: color-mix(in srgb, var(--primary-color) 30%, transparent); color: var(--primary-text-color); }
.grip { position: absolute; top: 0; bottom: 0; width: 10px; cursor: ew-resize; }
.grip.l { left: 0; }
.grip.r { right: 0; }
.handle { position: absolute; top: 0; bottom: 0; width: ${HANDLE}px; display: flex; align-items: center; cursor: ew-resize; touch-action: none; user-select: none; z-index: 3; --mdc-icon-size: 18px; }
.handle.start { justify-content: flex-end; }
.handle ha-icon { display: flex; align-items: center; height: 34px; border-radius: 6px; background: var(--primary-color); color: var(--text-primary-color, #fff); }
.bubble { position: fixed; z-index: 50; background: var(--primary-text-color); color: var(--card-background-color); padding: 4px 8px; border-radius: 6px; font-size: 12px;
  pointer-events: none; transform: translate(-50%, -140%); white-space: nowrap; }
.flows .axis-all { position: relative; height: 18px; }
.flows .axis-all span { position: absolute; font-size: 11px; color: var(--secondary-text-color); }
.flow { display: grid; grid-template-columns: 170px minmax(0, 1fr); align-items: stretch; width: 100%; padding: 0; min-height: 48px; border: 0; border-top: 1px solid var(--divider-color); border-radius: 0; text-align: left; }
.flow.sel { background: color-mix(in srgb, var(--primary-color) 14%, transparent); }
.flow-name { padding: 4px 8px; line-height: 1.3; font-weight: 500; font-size: 13px; overflow-wrap: break-word; hyphens: auto; min-width: 0; }
.flow-name .muted { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; font-weight: 400; font-size: 11px; --mdc-icon-size: 14px; }
.flow-axis { display: grid; grid-template-columns: 170px minmax(0, 1fr); }
.dot { color: var(--primary-color); }
.mini { position: relative; overflow: hidden; min-height: 48px; }
.mini div { position: absolute; border-radius: 2px; }
.mini.off div { opacity: .35; }
.now { position: absolute; top: 0; bottom: 0; width: 2px; background: var(--error-color); }
.inline { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
.inline select { flex: 1; min-width: 140px; width: auto; }
.inline select.type { flex: 0 0 110px; min-width: 0; }
.days { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 12px; }
.days button { font-size: 12px; padding: 4px 10px; }
.days button[aria-pressed=true] { background: var(--primary-color); border-color: var(--primary-color); color: var(--text-primary-color, #fff); }
.where { display: block; font-size: 11px; color: var(--secondary-text-color); }
.chips { display: flex; gap: 6px; flex-wrap: wrap; }
.chip { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; padding: 3px 4px 3px 10px; border-radius: 8px;
  background: color-mix(in srgb, var(--primary-color) 18%, transparent); }
.chip button { border: 0; padding: 0 6px; min-height: 22px; line-height: 1; font-size: 15px; }
.hint { font-size: 12px; color: var(--secondary-text-color); margin: 8px 0 0; }
.field-icon { display: inline-flex; align-items: center; gap: 4px; --mdc-icon-size: 15px; }
.detail { margin-top: 12px; padding-top: 4px; border-top: 1px solid var(--divider-color); }
details.legend { margin-top: 12px; font-size: 13px; }
details.legend summary { cursor: pointer; color: var(--secondary-text-color); font-size: 12px; font-weight: 500; }
.legend-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 6px 16px; margin-top: 8px; --mdc-icon-size: 18px; }
.legend-grid h3 { grid-column: 1 / -1; font-size: 12px; font-weight: 500; color: var(--secondary-text-color); margin: 8px 0 0; }
.legend-grid div { display: flex; align-items: center; gap: 8px; min-width: 0; }
.look { display: flex; flex-direction: column; gap: 10px; }
.modes { display: inline-flex; flex-wrap: wrap; gap: 4px; }
.modes button { font-size: 12px; padding: 4px 10px; }
.modes button[aria-pressed=true] { background: var(--primary-color); border-color: var(--primary-color); color: var(--text-primary-color, #fff); }
.swatches { display: flex; flex-wrap: wrap; gap: 6px; }
.wheel { position: relative; width: min(100%, 240px); aspect-ratio: 1; border-radius: 50%; cursor: crosshair; touch-action: none;
  background: radial-gradient(closest-side, #fff, transparent), conic-gradient(from 90deg, #f00, #ff0, #0f0, #0ff, #00f, #f0f, #f00); }
.wheel:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 2px; }
.wheel i { position: absolute; width: 28px; height: 28px; margin: -14px 0 0 -14px; box-sizing: border-box; border: 3px solid #fff; border-radius: 50%; pointer-events: none; box-shadow: 0 1px 4px rgba(0, 0, 0, .6); }
.swatches button { width: 28px; height: 28px; min-height: 0; padding: 0; border-radius: 50%; }
.summary { font-size: 14px; line-height: 1.6; margin: 0; }
.summary ul { margin: 4px 0; padding-left: 18px; }
.plain { border-top: 1px solid var(--divider-color); margin-top: 18px; }
.actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 16px; }
.actions .status { margin-right: auto; }
.error { color: var(--error-color); font-size: 13px; margin: 6px 0 0; }
.sim-head { display: flex; align-items: flex-end; gap: 12px; flex-wrap: wrap; }
.sim-head .days { margin: 4px 0 0; }
.sim-time { display: flex; align-items: flex-end; gap: 8px; }
.sim-time input { width: 110px; }
input.sim-slider { -webkit-appearance: none; appearance: none; display: block; height: 32px; margin: 8px 0 0; padding: 0; background: transparent; --pos: 0%; }
input.sim-slider::-webkit-slider-runnable-track { height: 6px; border-radius: 3px; background: linear-gradient(to right, var(--primary-color) var(--pos), var(--divider-color) var(--pos)); }
input.sim-slider::-moz-range-track { height: 6px; border-radius: 3px; background: linear-gradient(to right, var(--primary-color) var(--pos), var(--divider-color) var(--pos)); }
input.sim-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 20px; height: 20px; margin-top: -7px; border-radius: 50%; background: var(--primary-color); }
input.sim-slider::-moz-range-thumb { width: 20px; height: 20px; border: 0; border-radius: 50%; background: var(--primary-color); }
.sim-tiles { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 8px; margin-top: 8px; }
.sim-tile { display: flex; align-items: center; gap: 12px; min-width: 0; padding: 8px 12px; border: 1px solid var(--divider-color); border-radius: var(--ha-card-border-radius, 12px); }
.sim-badge { flex: none; display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border-radius: 50%; color: var(--tint); background: color-mix(in srgb, var(--tint) 20%, transparent); --mdc-icon-size: 20px; }
.sim-text { min-width: 0; font-size: 14px; font-weight: 500; line-height: 1.3; }
.sim-text > * { display: block; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.sim-text small { font-size: 12px; font-weight: 400; color: var(--secondary-text-color); }
.empty { text-align: center; padding: 32px 16px; }
.empty h2 { font-size: 18px; font-weight: 500; margin: 0 0 8px; }
.empty p { color: var(--secondary-text-color); margin: 0 auto 16px; max-width: 420px; }
@media (pointer: coarse) {
  .grip { display: none; }
  .track { height: 56px; }
}
@media (max-width: 600px) {
  main { padding: 8px; }
  .lines { min-width: 640px; }
  .line, .flow, .flow-axis { grid-template-columns: 124px minmax(0, 1fr); }
  .line-name:not(.sel) button { display: none; }
}
`;

function h(tag, props = {}, ...children) {
  const element = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (key.startsWith("on")) element.addEventListener(key.slice(2), value);
    else if (key === "class") element.className = value;
    else if (key === "style") element.style.cssText = value;
    else if (key in element && key !== "list") element[key] = value;
    else element.setAttribute(key, value);
  }
  for (const child of children.flat()) {
    if (child !== null && child !== undefined) element.append(child);
  }
  return element;
}

function clockOf(date) {
  return `${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
}

function isTouch() {
  return matchMedia("(pointer: coarse)").matches;
}

function hsToRgb(hue, saturation) {
  const channel = (n) => {
    const k = (n + hue / 60) % 6;
    return Math.round(255 * (1 - saturation * Math.max(0, Math.min(k, 4 - k, 1))));
  };
  return [channel(5), channel(3), channel(1)];
}

function rgbToHs([r, g, b]) {
  const max = Math.max(r, g, b);
  const delta = max - Math.min(r, g, b);
  if (!delta) return [0, 0];
  let hue;
  if (max === r) hue = (g - b) / delta;
  else if (max === g) hue = (b - r) / delta + 2;
  else hue = (r - g) / delta + 4;
  return [mod(hue * 60, 360), delta / max];
}

function kelvinToRgb(kelvin) {
  const share = Math.min(1, Math.max(0, (kelvin - 2000) / 4500));
  const warm = [255, 170, 90];
  const cool = [215, 228, 255];
  return warm.map((v, i) => Math.round(v + (cool[i] - v) * share));
}

function hueName(rgb) {
  const [r, g, b] = rgb.map((v) => v / 255);
  const max = Math.max(r, g, b);
  const delta = max - Math.min(r, g, b);
  if (max === 0 || delta / max < 0.15) return "white.neutral";
  let hue;
  if (max === r) hue = ((g - b) / delta + 6) % 6;
  else if (max === g) hue = (b - r) / delta + 2;
  else hue = (r - g) / delta + 4;
  hue *= 60;
  if (hue < 15 || hue >= 345) return "hue.red";
  if (hue < 45) return "hue.orange";
  if (hue < 70) return "hue.yellow";
  if (hue < 165) return "hue.green";
  if (hue < 200) return "hue.cyan";
  if (hue < 260) return "hue.blue";
  if (hue < 300) return "hue.purple";
  return "hue.pink";
}

function whiteName(kelvin) {
  if (kelvin < 3300) return "white.warm";
  return kelvin < 5000 ? "white.neutral" : "white.cool";
}

function lookColors(look) {
  if (look.mode === "keep") return ["var(--secondary-background-color)", "var(--primary-text-color)"];
  const rgb = look.mode === "white" ? kelvinToRgb(look.kelvin) : look.rgb;
  const luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255;
  return [`rgb(${rgb.join(",")})`, luminance > 0.55 ? "#1a1a1a" : "#ffffff"];
}

function randomId() {
  return Array.from({ length: 16 }, () => Math.floor(Math.random() * 16).toString(16)).join("");
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function newLook() {
  return { mode: "white", kelvin: 2700, rgb: [255, 255, 255], brightness: 80 };
}

const TARGET_KEYS = ["entity_id", "device_id", "area_id", "floor_id", "label_id"];
const DAY = 1440;
const SNAP = 5;
const SHORTEST = 15;

const ICONS = {
  start: {
    time: "mdi:clock-outline",
    sunset: "mdi:weather-sunset-down",
    sunrise: "mdi:weather-sunset-up",
    sun_elevation: "mdi:angle-acute",
  },
  at_start: { turn_on: "mdi:lightbulb-on-outline", adjust: "mdi:tune" },
  look: { off: "mdi:power", unchanged: "mdi:hand-back-right-off-outline" },
  at_end: { turn_off: "mdi:power", restore: "mdi:undo" },
  condition: {
    always: "mdi:account-off-outline",
    anyone_home: "mdi:home-account",
    everyone_home: "mdi:account-group",
    nobody_home: "mdi:home-export-outline",
    person: "mdi:account",
  },
  on_arrival: { apply: "mdi:home-import-outline", nothing: "mdi:cancel" },
  respect_manual: "mdi:hand-back-right",
  type: {
    light: "mdi:lightbulb-outline",
    device: "mdi:devices",
    area: "mdi:sofa-outline",
    floor: "mdi:floor-plan",
    label: "mdi:label-outline",
    scene: "mdi:palette-outline",
    several: "mdi:format-list-bulleted",
  },
};

function ensureList(value) {
  if (value === undefined || value === null) return [];
  return Array.isArray(value) ? value : [value];
}

function cleanTarget(value) {
  const clean = (source) =>
    Object.fromEntries(
      TARGET_KEYS.filter((key) => ensureList(source?.[key]).length).map((key) => [key, ensureList(source[key])])
    );
  const target = clean(value);
  const exclude = clean(value?.exclude);
  return Object.keys(exclude).length ? { ...target, exclude } : target;
}

function icon(name, title) {
  return h("ha-icon", title ? { icon: name, title } : { icon: name });
}

function mod(value, base = DAY) {
  return ((value % base) + base) % base;
}

function toMinutes(text) {
  const [hours, minutes] = text.split(":").map(Number);
  return hours * 60 + minutes;
}

function toClock(minutes) {
  const value = mod(Math.round(minutes));
  return `${String(Math.floor(value / 60)).padStart(2, "0")}:${String(value % 60).padStart(2, "0")}`;
}

function snap(minutes) {
  return Math.round(minutes / SNAP) * SNAP;
}

class LightPlannerPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._ready = false;
    this._flows = [];
    this._saved = {};
    this._selected = null;
    this._selectedBar = null;
    this._selectedRow = null;
    this._options = { light: [], area: [], label: [], scene: [], person: [] };
    this._preview = null;
    this._previewSeq = 0;
    this._drag = null;
    const now = new Date();
    this._pvDay = (now.getDay() + 6) % 7;
    this._pvTime = clockOf(now);
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._ready) {
      this._ready = true;
      this._init();
    }
    this.style.colorScheme = hass.themes?.darkMode ? "dark" : "light";
    for (const picker of this.shadowRoot.querySelectorAll("ha-selector")) picker.hass = hass;
  }

  set narrow(narrow) {
    this._narrow = narrow;
    if (this._menu) this._menu.hidden = !narrow;
  }

  set panel(_panel) {}

  set route(_route) {}

  // Texts

  get _language() {
    const language = this._hass?.language ?? "en";
    return [language, language.split("-")[0]].find((code) => I18N[code]) ?? "en";
  }

  _t(key, vars = {}) {
    const text = I18N[this._language][key] ?? I18N.en[key] ?? key;
    return text.replace(/\{(\w+)\}/g, (_, name) => vars[name] ?? "");
  }

  get _locale() {
    return this._language;
  }

  _plural(prefix, count) {
    const rule = new Intl.PluralRules(this._locale).select(count);
    return this._t(`${prefix}_${rule === "one" ? "one" : "other"}`, { count });
  }

  _list(items) {
    return new Intl.ListFormat(this._locale, { style: "long", type: "conjunction" }).format(items);
  }

  get _dayNames() {
    const format = new Intl.DateTimeFormat(this._locale, { weekday: "short" });
    return [...Array(7).keys()].map((i) => format.format(new Date(2024, 0, 1 + i)));
  }

  _daysText(days) {
    const sorted = [...days].sort();
    if (sorted.length === 7) return this._t("days.all");
    if (sorted.join() === "0,1,2,3,4") return this._t("days.weekdays");
    if (sorted.join() === "5,6") return this._t("days.weekend");
    return this._list(sorted.map((d) => this._dayNames[d]));
  }

  _nameOf(type, id) {
    return this._options[type].find((item) => item.id === id)?.name ?? id;
  }

  // Names like Home Assistant's own pickers: the entity's name, then "Area ▸ Device".
  _entityParts(entityId) {
    const state = this._hass.states[entityId];
    const part = (type) => (state && this._hass.formatEntityName?.(state, { type })) || "";
    const entity = part("entity");
    const device = part("device");
    const area = part("area");
    const friendly = state?.attributes.friendly_name;
    // A light without its own name reports its device's name as the entity's name too.
    const ownDevice = entity && entity !== device ? device : "";
    const secondary = [area, part("parent_device"), ownDevice].filter(Boolean).join(" ▸ ");
    return { primary: entity || device || friendly || entityId, secondary, area, device };
  }

  _entityLabel(entityId) {
    const { primary, secondary } = this._entityParts(entityId);
    return secondary ? `${primary} (${secondary})` : primary;
  }

  _lookPhrase(look) {
    const percent = look.brightness;
    if (look.mode === "keep") {
      return percent === null ? this._t("s.look_on") : this._t("s.look_on_percent", { percent });
    }
    const name = this._t(look.mode === "white" ? whiteName(look.kelvin) : hueName(look.rgb));
    return percent === null
      ? this._t("s.look_named", { look: name })
      : this._t("s.look_named_percent", { look: name, percent });
  }

  _lookLabel(look) {
    if (look.mode === "off") return this._t("off");
    if (look.mode === "unchanged") return this._t("look_mode.unchanged");
    const phrase = this._lookPhrase(look);
    return phrase.charAt(0).toUpperCase() + phrase.slice(1);
  }

  _sunText(anchor) {
    const sun = this._t(`s.sun.${anchor.type}`);
    if (!anchor.offset) return sun;
    return this._t(anchor.offset > 0 ? "s.after" : "s.before", { minutes: Math.abs(anchor.offset), sun });
  }

  _startText(start) {
    if (start.type === "time") return start.time || "?";
    const text =
      start.type === "sun_elevation"
        ? this._t("s.elevation", { deg: start.elevation ?? "?" })
        : this._sunText(start);
    return start.time ? this._t("s.not_before", { start: text, time: start.time }) : text;
  }

  _endText(end) {
    return end.type === "time" ? end.time || "?" : this._sunText(end);
  }

  _targetItems(target) {
    const types = { device_id: "device", area_id: "area", floor_id: "floor", label_id: "label" };
    return TARGET_KEYS.flatMap((key) =>
      ensureList(target?.[key]).map((id) => ({
        type: key === "entity_id" ? (id.startsWith("scene.") ? "scene" : "light") : types[key],
        id,
      }))
    );
  }

  _onlyScenes(row) {
    const items = this._targetItems(row.target);
    return items.length > 0 && items.every((item) => item.type === "scene");
  }

  _deviceArea(id) {
    const device = this._hass.devices?.[id];
    return (device?.area_id && this._hass.areas?.[device.area_id]?.name) || "";
  }

  _itemName({ type, id }) {
    if (type === "light" || type === "scene") return this._entityParts(id).primary;
    if (type === "device") {
      const device = this._hass.devices?.[id];
      return device?.name_by_user || device?.name || id;
    }
    if (type === "area") return this._hass.areas?.[id]?.name ?? this._nameOf("area", id);
    if (type === "floor") return this._hass.floors?.[id]?.name ?? id;
    return this._nameOf("label", id);
  }

  _itemText(item) {
    const name = this._itemName(item);
    if (item.type === "light" || item.type === "scene") {
      const { area, device } = this._entityParts(item.id);
      const where = area || (device !== name ? device : "");
      return where ? `${name} (${where})` : name;
    }
    if (item.type === "device") {
      const area = this._deviceArea(item.id);
      return area ? `${name} (${area})` : name;
    }
    return this._t(`s.${item.type}`, { name });
  }

  _targetText(row) {
    const names = this._list(this._targetItems(row.target).map((item) => this._itemText(item)));
    const excluded = this._targetItems(row.target.exclude).map((item) => this._itemText(item));
    if (!excluded.length) return names;
    return this._t("s.without", { names, excluded: this._list(excluded) });
  }

  _barSentence(row, bar) {
    const vars = {
      who: this._targetText(row),
      start: this._startText(bar.start),
      end: this._endText(bar.end),
      look: bar.look.mode === "off" || bar.look.mode === "unchanged" ? "" : this._lookPhrase(bar.look),
    };
    let key = "s.bar_on";
    if (this._onlyScenes(row)) key = "s.bar_scene";
    else if (bar.look.mode === "off") key = "s.bar_off";
    else if (bar.look.mode === "unchanged") key = "s.bar_unchanged";
    else if (bar.at_start === "adjust") {
      key = bar.look.mode === "keep" && bar.look.brightness === null ? "s.bar_keep" : "s.bar_adjust";
    }
    let after = "";
    if (bar.look.mode !== "unchanged") {
      if (bar.at_end === "restore") after = this._t("s.then_restore");
      else if (bar.at_end === "turn_off" && bar.look.mode !== "off") after = this._t("s.then_off");
    }
    const sentence = `${this._t(key, vars)}${after}.`;
    return sentence.charAt(0).toUpperCase() + sentence.slice(1);
  }

  _renderSummary(flow) {
    const bars = flow.rows.flatMap((row) => row.bars.map((bar) => [this._span(bar)[0], row, bar]));
    if (!flow.days.length) return [this._t("s.pick_day")];
    if (!bars.length) return [this._t("s.no_bars")];
    const hour = this._axisHour(flow);
    bars.sort((a, b) => this._relative(a[0], hour) - this._relative(b[0], hour));
    const person = flow.person ? this._nameOf("person", flow.person) : "?";
    const intro = this._t("s.intro", {
      days: this._daysText(flow.days),
      condition: this._t(`s.cond.${flow.condition}`, { person }),
    });
    return [
      intro,
      h("ul", {}, bars.map(([, row, bar]) => h("li", {}, this._barSentence(row, bar)))),
      flow.condition === "nobody_home"
        ? null
        : this._t(flow.on_arrival === "apply" ? "s.arrival_apply" : "s.arrival_nothing"),
      flow.respect_manual ? h("div", {}, this._t("s.manual", { hours: flow.manual_hours })) : null,
    ];
  }

  // Data

  async _init() {
    const root = this.shadowRoot;
    this._menu = h(
      "button",
      {
        "aria-label": "Menu",
        hidden: !this._narrow,
        onclick: () => this.dispatchEvent(new Event("hass-toggle-menu", { bubbles: true, composed: true })),
      },
      "☰"
    );
    this._flowsEl = h("div");
    this._showingEl = h("span", { class: "muted" });
    this._editorEl = h("div");
    this._previewEl = h("div", { class: "card" });
    this._pageError = h("p", { class: "error" });
    root.replaceChildren(
      h("style", {}, STYLE),
      h("header", {}, this._menu, this._t("title")),
      h(
        "main",
        {},
        this._pageError,
        h(
          "div",
          { class: "card flows" },
          h(
            "div",
            { class: "head" },
            h("div", {}, h("div", {}, this._t("flows")), this._showingEl),
            h("button", { class: "primary", onclick: () => this._addFlow() }, `+ ${this._t("new_flow")}`)
          ),
          h(
            "div",
            { class: "flow-axis" },
            h("div"),
            h(
              "div",
              { class: "axis-all" },
              [0, 6, 12, 18, 24].map((hour) =>
                h(
                  "span",
                  {
                    style: `left:${(hour / 24) * 100}%;transform:translateX(${hour === 24 ? "-100%" : hour === 0 ? "0" : "-50%"})`,
                  },
                  String(hour)
                )
              )
            )
          ),
          this._flowsEl
        ),
        this._editorEl,
        this._previewEl
      )
    );
    this._buildPreviewControls();
    try {
      const [options, list] = await Promise.all([
        this._hass.callWS({ type: "light_planner/options" }),
        this._hass.callWS({ type: "light_planner/list" }),
      ]);
      this._options = options;
      this._flows = list.flows.map(clone);
      for (const flow of list.flows) this._saved[flow.id] = JSON.stringify(flow);
      this._selected = this._flows[0]?.id ?? null;
    } catch (err) {
      this._pageError.textContent = err.message;
    }
    this._renderFlows();
    this._renderEditor();
    this._requestPreview();
  }

  get _current() {
    return this._flows.find((f) => f.id === this._selected) ?? null;
  }

  _isDirty(flow) {
    return this._saved[flow.id] !== JSON.stringify(flow);
  }

  _addFlow() {
    const flow = {
      id: randomId(),
      name: this._t("default_name"),
      enabled: true,
      days: [0, 1, 2, 3, 4, 5, 6],
      condition: "always",
      person: null,
      on_arrival: "apply",
      respect_manual: false,
      manual_hours: 4,
      rows: [],
    };
    this._flows.push(flow);
    this._selected = flow.id;
    this._selectedBar = null;
    this._selectedRow = null;
    this._renderFlows();
    this._renderEditor();
    this._requestPreview();
  }

  _select(id) {
    this._selected = id;
    this._selectedBar = null;
    this._selectedRow = null;
    this._renderFlows();
    this._renderEditor();
    this._syncSimulation();
  }

  _changed() {
    this._renderFlows();
    this._renderTimeline();
    this._refreshEditorState();
    this._renderPreviewResult();
    this._requestPreview();
  }

  // Merged, not restarted: while the slider moves, every round trip shows the latest time.
  _requestPreview() {
    if (this._previewLoading) {
      this._previewAgain = true;
      return;
    }
    this._previewTimer ??= setTimeout(() => {
      this._previewTimer = null;
      this._loadPreview();
    }, 40);
  }

  async _loadPreview() {
    const seq = ++this._previewSeq;
    this._previewLoading = true;
    try {
      const result = await this._hass.callWS({
        type: "light_planner/preview",
        flows: this._flows,
        weekday: this._pvDay,
        time: this._pvTime,
      });
      if (seq !== this._previewSeq) return;
      this._preview = result;
      this._pageError.textContent = "";
      this._renderFlows();
      this._renderPreviewResult();
      if (!this._drag) this._renderTimeline();
      this._refreshEditorState();
      if (JSON.stringify(result.flows?.[this._selected]?.manual ?? []) !== this._manualShown) {
        this._manualShown = JSON.stringify(result.flows?.[this._selected]?.manual ?? []);
        this._renderManual();
      }
    } catch (err) {
      this._pageError.textContent = err.message;
    } finally {
      this._previewLoading = false;
      if (this._previewAgain) {
        this._previewAgain = false;
        this._requestPreview();
      }
    }
  }

  async _save() {
    const flow = this._current;
    if (!flow) return;
    this._error("");
    try {
      const result = await this._hass.callWS({ type: "light_planner/save", flow });
      Object.assign(flow, result.flow);
      this._saved[flow.id] = JSON.stringify(flow);
      this._renderFlows();
      this._refreshEditorState();
      this._requestPreview();
    } catch (err) {
      this._error(err.message);
    }
  }

  async _applyNow(button) {
    this._error("");
    try {
      await this._hass.callWS({ type: "light_planner/apply_now", flow: this._current });
      button.textContent = this._t("applied");
      setTimeout(() => (button.textContent = this._t("apply_now")), 1500);
    } catch (err) {
      this._error(err.message);
    }
  }

  async _delete(button) {
    if (!button.dataset.armed) {
      button.dataset.armed = "1";
      button.textContent = this._t("delete_confirm");
      setTimeout(() => {
        delete button.dataset.armed;
        button.textContent = this._t("delete");
      }, 4000);
      return;
    }
    const flow = this._current;
    try {
      if (this._saved[flow.id]) {
        await this._hass.callWS({ type: "light_planner/delete", flow_id: flow.id });
      }
      delete this._saved[flow.id];
      this._flows = this._flows.filter((f) => f.id !== flow.id);
      this._selected = this._flows[0]?.id ?? null;
      this._selectedBar = null;
      this._selectedRow = null;
      this._renderFlows();
      this._renderEditor();
      this._requestPreview();
    } catch (err) {
      this._error(err.message);
    }
  }

  _discard() {
    const flow = this._current;
    const saved = this._saved[flow.id];
    if (!saved) return;
    this._flows[this._flows.indexOf(flow)] = JSON.parse(saved);
    this._selectedBar = null;
    this._selectedRow = null;
    this._renderFlows();
    this._renderEditor();
    this._requestPreview();
  }

  _error(text) {
    text = I18N[this._language][`err.${text}`] ?? text;
    if (this._errorEl) this._errorEl.textContent = text;
  }

  // Times on the timeline, all in minutes of the simulated day

  _sunMinutes(kind) {
    const hours = this._preview?.sun?.[kind];
    if (hours !== null && hours !== undefined) return hours * 60;
    return kind === "sunset" ? 18 * 60 : 6 * 60;
  }

  _belowMinutes(degrees) {
    const points = this._preview?.sun?.below ?? [];
    if (!points.length) return this._sunMinutes("sunset");
    let lower = points[0];
    let upper = points[points.length - 1];
    for (const point of points) {
      if (point[0] <= degrees && point[0] >= lower[0]) lower = point;
      if (point[0] >= degrees && point[0] <= upper[0]) upper = point;
    }
    if (lower[0] === upper[0]) return lower[1] * 60;
    const share = (degrees - lower[0]) / (upper[0] - lower[0]);
    return (lower[1] + (upper[1] - lower[1]) * share) * 60;
  }

  _degreesAt(minutes) {
    const points = this._preview?.sun?.below ?? [];
    if (!points.length) return 12;
    let best = points[0];
    let next = null;
    for (const point of points) {
      if (Math.abs(point[1] * 60 - minutes) < Math.abs(best[1] * 60 - minutes)) best = point;
    }
    for (const point of points) {
      const between = (point[1] * 60 - minutes) * (best[1] * 60 - minutes) < 0;
      if (between && (!next || Math.abs(point[1] * 60 - minutes) < Math.abs(next[1] * 60 - minutes))) next = point;
    }
    if (!next) return best[0];
    const share = (minutes - best[1] * 60) / ((next[1] - best[1]) * 60);
    return Math.round((best[0] + (next[0] - best[0]) * share) * 2) / 2;
  }

  _startMinutes(start) {
    if (start.type === "time") return start.time ? toMinutes(start.time) : null;
    const base = start.type === "sun_elevation" ? this._belowMinutes(start.elevation ?? 12) : this._sunMinutes(start.type);
    const moment = base + (start.offset ?? 0);
    return start.time ? Math.max(moment, toMinutes(start.time)) : moment;
  }

  _endMinutes(end) {
    if (end.type === "time") return end.time ? toMinutes(end.time) : null;
    return this._sunMinutes(end.type) + (end.offset ?? 0);
  }

  _span(bar) {
    const start = mod(this._startMinutes(bar.start) ?? 18 * 60);
    let end = this._endMinutes(bar.end) ?? start + 60;
    end = mod(end);
    if (end <= start) end += DAY;
    return [start, end];
  }

  _axisHour(flow) {
    const spans = flow.rows.flatMap((row) => row.bars.map((bar) => this._span(bar)));
    const crosses = (hour) =>
      spans.some(([start, end]) =>
        [hour * 60, hour * 60 + DAY].some((moment) => start < moment && moment < end)
      );
    for (let distance = 0; distance < 12; distance++) {
      for (const hour of [mod(12 + distance, 24), mod(12 - distance, 24)]) {
        if (!crosses(hour)) return hour;
      }
    }
    return 12;
  }

  _relative(minutes, hour) {
    return mod(minutes - hour * 60);
  }

  _setAnchor(anchor, minutes, isStart) {
    if (anchor.type === "time") {
      anchor.time = toClock(snap(minutes));
    } else if (anchor.type === "sun_elevation") {
      anchor.elevation = this._degreesAt(mod(minutes));
    } else {
      let moment = mod(minutes);
      if (isStart && anchor.time) moment = Math.max(moment, toMinutes(anchor.time));
      const offset = mod(moment - this._sunMinutes(anchor.type) + 720) - 720;
      anchor.offset = Math.max(-720, Math.min(720, snap(offset)));
    }
  }

  // Flow list

  _paint(row, bar) {
    if (this._onlyScenes(row)) return ["paint-scene", ""];
    if (bar.look.mode === "off") return ["paint-off", ""];
    if (bar.look.mode === "unchanged") return ["paint-unchanged", ""];
    const [background, color] = lookColors(bar.look);
    return ["", `background:${background};color:${color};`];
  }

  _renderFlows() {
    this._showingEl.textContent = this._t("showing", { day: this._dayNames[this._pvDay] });
    const today = (new Date().getDay() + 6) % 7;
    const now = new Date();
    const nowHours = now.getHours() + now.getMinutes() / 60;
    this._flowsEl.replaceChildren(
      ...this._flows.map((flow) => {
        const details = this._preview?.flows?.[flow.id];
        const height = 40 / Math.max(1, flow.rows.length);
        const marks = flow.rows.flatMap((row, index) =>
          row.bars.flatMap((bar) =>
            (details?.bars?.[bar.id] ?? []).map(([from, to]) => {
              const [paint, style] = this._paint(row, bar);
              return h("div", {
                class: paint,
                style: `${style}left:${(from / 24) * 100}%;width:${((to - from) / 24) * 100}%;top:${4 + index * height}px;height:${Math.max(3, height - 1)}px`,
              });
            })
          )
        );
        const conditionText = this._t(`condition.${flow.condition}`);
        return h(
          "button",
          {
            class: `flow${flow.id === this._selected ? " sel" : ""}`,
            onclick: () => this._select(flow.id),
          },
          h(
            "div",
            { class: "flow-name" },
            flow.name.trim() || this._t("unnamed"),
            this._isDirty(flow) ? h("span", { class: "dot", title: this._t("unsaved") }, " ●") : null,
            h(
              "span",
              { class: "muted" },
              icon(ICONS.condition[flow.condition], conditionText),
              flow.condition === "nobody_home"
                ? null
                : icon(ICONS.on_arrival[flow.on_arrival], `${this._t("on_arrival")}: ${this._t(`on_arrival.${flow.on_arrival}`)}`),
              flow.respect_manual ? icon(ICONS.respect_manual, this._t("respect_manual")) : null,
              `${this._plural("row", flow.rows.length)} · ${this._daysText(flow.days)}`
            )
          ),
          h(
            "div",
            { class: `mini${flow.enabled ? "" : " off"}` },
            marks,
            this._pvDay === today ? h("div", { class: "now", style: `left:${(nowHours / 24) * 100}%` }) : null
          )
        );
      })
    );
  }

  // Editor

  _select_(label, value, options, onchange) {
    const select = h(
      "select",
      { onchange: (e) => onchange(e.target.value) },
      options.map(([id, text]) => h("option", { value: id, selected: id === value }, text))
    );
    select.value = value ?? "";
    return label ? h("label", { class: "fld" }, label, select) : select;
  }

  _options_(prefix, ids) {
    return ids.map((id) => [id, this._t(`${prefix}.${id}`)]);
  }

  _fieldLabel(iconName, text) {
    return h("span", { class: "field-icon" }, icon(iconName), text);
  }

  _renderNoFlow() {
    this._errorEl = null;
    this._summaryEl = null;
    this._linesEl = null;
    this._editorEl.replaceChildren(
      h(
        "div",
        { class: "card empty" },
        h("h2", {}, this._t("empty_title")),
        h("p", {}, this._t("empty_body")),
        h("button", { class: "primary", onclick: () => this._addFlow() }, `+ ${this._t("new_flow")}`)
      )
    );
  }

  _flowHead(flow) {
    const name = h("input", {
      type: "text",
      value: flow.name,
      placeholder: this._t("name_placeholder"),
      oninput: (e) => {
        flow.name = e.target.value;
        this._renderFlows();
        this._refreshEditorState();
      },
    });
    const enabled = h("input", {
      type: "checkbox",
      checked: flow.enabled,
      onchange: (e) => {
        flow.enabled = e.target.checked;
        this._changed();
      },
    });
    return h(
      "div",
      { class: "head" },
      h("label", { class: "fld", style: "flex:1;min-width:200px" }, this._t("name"), name),
      h("label", { class: "check" }, enabled, this._t("enabled"))
    );
  }

  _flowActions() {
    return h(
      "div",
      { class: "actions" },
      this._statusEl,
      h("button", { class: "danger", onclick: (e) => this._delete(e.currentTarget) }, this._t("delete")),
      h(
        "button",
        { title: this._t("apply_now_title"), onclick: (e) => this._applyNow(e.currentTarget) },
        this._t("apply_now")
      ),
      this._discardBtn,
      this._saveBtn
    );
  }

  _renderEditor() {
    const flow = this._current;
    if (!flow) {
      this._renderNoFlow();
      return;
    }
    this._daysEl = h("div", { class: "days" });
    this._behaviorEl = h("div", { class: "grid" });
    this._manualEl = h("div", {});
    this._linesEl = h("div", { class: "lines" });
    this._detailEl = h("div", { class: "detail" });
    this._summaryEl = h("div", { class: "summary" });
    this._errorEl = h("p", { class: "error" });
    this._statusEl = h("span", { class: "muted status" });
    this._saveBtn = h("button", { class: "primary", onclick: () => this._save() }, this._t("save"));
    this._discardBtn = h("button", { onclick: () => this._discard() }, this._t("discard"));

    this._targetType = "light";
    this._targetTypeEl = this._select_(null, "light", this._options_("type", ["light", "area", "label", "scene"]), (value) => {
      this._targetType = value;
      this._fillTargetChoices();
    });
    this._targetTypeEl.classList.add("type");
    this._targetChoiceEl = h("select", { "aria-label": this._t("row_target") });

    this._editorEl.replaceChildren(
      h(
        "div",
        { class: "card" },
        this._flowHead(flow),
        this._behaviorEl,
        this._daysEl,
        this._manualEl,
        h("div", { class: "sec" }, this._t("timeline")),
        h("p", { class: "hint", style: "margin:0 0 8px" }, this._t(isTouch() ? "timeline_hint_touch" : "timeline_hint")),
        h("div", { class: "scroll" }, this._linesEl),
        this._addRowArea(),
        h("p", { class: "hint" }, this._t("own_row_hint")),
        this._detailEl,
        h("div", { class: "plain" }, h("div", { class: "sec" }, this._t("plain_words")), this._summaryEl),
        this._legend(),
        this._errorEl,
        this._flowActions()
      )
    );
    this._fillTargetChoices();
    this._renderBehavior();
    this._renderDays();
    this._renderManual();
    this._renderTimeline();
    this._renderDetail();
    this._refreshEditorState();
  }

  _renderManual() {
    const flow = this._current;
    if (!flow || !this._manualEl) return;
    const toggle = h("input", {
      type: "checkbox",
      checked: flow.respect_manual,
      onchange: (e) => {
        flow.respect_manual = e.target.checked;
        this._renderManual();
        this._changed();
      },
    });
    const children = [
      h(
        "label",
        { class: "check", style: "margin-top:12px" },
        toggle,
        this._fieldLabel(ICONS.respect_manual, this._t("respect_manual"))
      ),
    ];
    if (flow.respect_manual) {
      children.push(
        h("p", { class: "hint" }, this._t("manual_hint")),
        h(
          "label",
          { class: "fld", style: "margin-top:8px;max-width:320px" },
          this._t("manual_hours"),
          h("input", {
            type: "number",
            min: 1,
            max: 24,
            step: 1,
            value: flow.manual_hours,
            onchange: (e) => {
              flow.manual_hours = Math.max(1, Math.min(24, Math.round(Number(e.target.value) || 4)));
              e.target.value = flow.manual_hours;
              this._changed();
            },
          })
        )
      );
      const lights = this._preview?.flows?.[flow.id]?.manual ?? [];
      if (lights.length) {
        const format = new Intl.DateTimeFormat(this._locale, { hour: "2-digit", minute: "2-digit" });
        children.push(
          h("div", { class: "sec" }, this._t("manual_now")),
          h(
            "div",
            { class: "chips" },
            lights.map((light) =>
              h(
                "span",
                { class: "chip" },
                this._t("manual_since", { name: this._entityLabel(light.id), time: format.format(new Date(light.at)) }),
                h(
                  "button",
                  {
                    "aria-label": this._t("manual_clear", { name: this._entityLabel(light.id) }),
                    title: this._t("manual_clear", { name: this._entityLabel(light.id) }),
                    onclick: () => this._clearManual(light.id),
                  },
                  "×"
                )
              )
            )
          )
        );
      }
    }
    this._manualEl.replaceChildren(...children);
  }

  async _clearManual(entityId) {
    this._error("");
    try {
      await this._hass.callWS({ type: "light_planner/clear_manual", entity_id: entityId });
      this._requestPreview();
    } catch (err) {
      this._error(err.message);
    }
  }

  _legend() {
    const item = (name, text) => h("div", {}, icon(name), h("span", {}, text));
    const group = (title, items) => [h("h3", {}, title), ...items];
    return h(
      "details",
      { class: "legend" },
      h("summary", {}, this._t("icons")),
      h(
        "div",
        { class: "legend-grid" },
        group(this._t("icons_when"), Object.entries(ICONS.start).map(([key, name]) => item(name, this._t(`start.${key}`)))),
        group(this._t("icons_what"), [
          item(ICONS.at_start.turn_on, this._t("at_start.turn_on")),
          item(ICONS.at_start.adjust, this._t("at_start.adjust")),
          item(ICONS.look.off, this._t("look_mode.off")),
          item(ICONS.look.unchanged, this._t("look_mode.unchanged")),
        ]),
        group(this._t("icons_after"), [
          item(ICONS.at_end.turn_off, this._t("at_end.turn_off")),
          item(ICONS.at_end.restore, this._t("at_end.restore")),
        ]),
        group(this._t("icons_condition"), Object.entries(ICONS.condition).map(([key, name]) => item(name, this._t(`condition.${key}`)))),
        group(this._t("icons_arrival"), Object.entries(ICONS.on_arrival).map(([key, name]) => item(name, this._t(`on_arrival.${key}`)))),
        group(this._t("respect_manual"), [item(ICONS.respect_manual, this._t("respect_manual"))]),
        group(this._t("icons_row"), Object.entries(ICONS.type).map(([key, name]) => item(name, this._t(`type.${key}`))))
      )
    );
  }

  _refreshEditorState() {
    const flow = this._current;
    if (!flow || !this._summaryEl) return;
    this._summaryEl.replaceChildren(...this._renderSummary(flow).filter(Boolean));
    const dirty = this._isDirty(flow);
    const known = Boolean(this._saved[flow.id]);
    this._statusEl.textContent = dirty ? this._t("unsaved") : this._t("saved");
    this._discardBtn.hidden = !dirty || !known;
    this._saveBtn.hidden = !dirty;
  }

  // Home Assistant's own target picker, like in automations. It only offers what can hold a
  // light or scene and brings "exclude" from 2026.11 on. Plain lists if it's ever missing.
  _targetPicker(value, onchange) {
    const picker = document.createElement("ha-selector");
    picker.hass = this._hass;
    picker.selector = { target: { entity: { domain: ["light", "scene"] } } };
    picker.value = value;
    picker.addEventListener("value-changed", (e) => onchange(cleanTarget(e.detail.value), picker));
    return picker;
  }

  _addRowArea() {
    if (customElements.get("ha-selector")) {
      return h(
        "div",
        { class: "add-row" },
        h("div", { class: "sec" }, this._t("add_row")),
        this._targetPicker(undefined, (target, picker) => {
          picker.value = undefined;
          if (!this._targetItems(target).length) return;
          const row = { id: randomId(), target, bars: [] };
          this._current.rows.push(row);
          this._selectedRow = row.id;
          this._selectedBar = null;
          this._renderDetail();
          this._changed();
        })
      );
    }
    customElements.whenDefined("ha-selector").then(() => this._renderEditor());
    return h(
      "div",
      { class: "inline" },
      this._targetTypeEl,
      this._targetChoiceEl,
      h("button", { onclick: () => this._addRow() }, `+ ${this._t("add_row")}`)
    );
  }

  _fillTargetChoices() {
    const entities = this._targetType === "light" || this._targetType === "scene";
    const items = (this._options[this._targetType] ?? [])
      .map((item) => ({ id: item.id, name: entities ? this._entityLabel(item.id) : item.name }))
      .sort((a, b) => a.name.localeCompare(b.name, this._locale));
    this._targetChoiceEl.replaceChildren(
      ...(items.length
        ? items.map((item) => h("option", { value: item.id }, item.name))
        : [h("option", { value: "" }, this._t("no_options"))])
    );
  }

  _addRow() {
    const flow = this._current;
    const id = this._targetChoiceEl.value;
    if (!id) return;
    const key = { light: "entity_id", scene: "entity_id", area: "area_id", label: "label_id" }[this._targetType];
    if (!flow.rows.some((r) => ensureList(r.target[key]).includes(id))) {
      flow.rows.push({ id: randomId(), target: { [key]: [id] }, bars: [] });
    }
    this._changed();
  }

  _removeRow(row) {
    const flow = this._current;
    flow.rows.splice(flow.rows.indexOf(row), 1);
    if (this._selectedRow === row.id) this._selectedRow = null;
    if (this._selectedBar && !this._findBar(this._selectedBar)) this._selectedBar = null;
    this._renderDetail();
    this._changed();
  }

  _findBar(barId) {
    for (const row of this._current?.rows ?? []) {
      const bar = row.bars.find((b) => b.id === barId);
      if (bar) return { row, bar };
    }
    return null;
  }

  _renderDays() {
    const flow = this._current;
    this._daysEl.replaceChildren(
      ...this._dayNames.map((name, index) =>
        h(
          "button",
          {
            "aria-pressed": String(flow.days.includes(index)),
            onclick: () => {
              flow.days = flow.days.includes(index)
                ? flow.days.filter((d) => d !== index)
                : [...flow.days, index].sort();
              this._renderDays();
              this._changed();
            },
          },
          name
        )
      )
    );
  }

  _renderBehavior() {
    const flow = this._current;
    const set = (key) => (value) => {
      flow[key] = value;
      this._renderBehavior();
      this._changed();
    };
    const fields = [
      this._select_(
        this._fieldLabel(ICONS.condition[flow.condition], this._t("only_when")),
        flow.condition,
        this._options_("condition", ["always", "anyone_home", "everyone_home", "nobody_home", "person"]),
        set("condition")
      ),
    ];
    if (flow.condition === "person") {
      const persons = this._options.person;
      if (!flow.person && persons.length) flow.person = persons[0].id;
      fields.push(
        this._select_(
          this._t("person"),
          flow.person,
          persons.length ? persons.map((p) => [p.id, p.name]) : [["", this._t("no_options")]],
          set("person")
        )
      );
    }
    if (flow.condition !== "nobody_home") {
      fields.push(
        this._select_(
          this._fieldLabel(ICONS.on_arrival[flow.on_arrival], this._t("on_arrival")),
          flow.on_arrival,
          this._options_("on_arrival", ["apply", "nothing"]),
          set("on_arrival")
        )
      );
    }
    this._behaviorEl.replaceChildren(...fields);
  }

  // Timeline

  _renderTimeline() {
    const flow = this._current;
    if (!flow || !this._linesEl || this._drag) return;
    const focused = this.shadowRoot.activeElement?.dataset?.bar;
    this._axis = this._axisHour(flow);
    this._barEls = new Map();
    const percent = (minutes) => (this._relative(minutes, this._axis) / DAY) * 100;
    const sunLines = () =>
      ["sunset", "sunrise"].map((kind) => h("i", { class: "sunline", style: `left:${percent(this._sunMinutes(kind))}%` }));
    const ticks = [...Array(12).keys()].map((index) =>
      h(
        "span",
        { class: `tick${index === 0 ? " first" : ""}`, style: `left:${(index / 12) * 100}%` },
        String(mod(this._axis + index * 2, 24)).padStart(2, "0")
      )
    );
    const sunMark = (kind) =>
      h(
        "span",
        { class: "sunmark", style: `left:${percent(this._sunMinutes(kind))}%` },
        icon(ICONS.start[kind]),
        toClock(this._sunMinutes(kind))
      );
    const axis = h(
      "div",
      { class: "line axis" },
      h("div", { class: "line-name" }),
      h("div", { class: "grid-track" }, ticks, sunMark("sunset"), sunMark("sunrise"))
    );
    this._simEls = [];
    const lines = flow.rows.map((row) => {
      const members = this._preview?.flows?.[flow.id]?.rows?.[row.id] ?? [];
      const items = this._targetItems(row.target);
      const single = items.length === 1 ? items[0] : null;
      const name = items.map((item) => this._itemName(item)).join(", ") || "?";
      let where = this._plural("light", members.length);
      if (single?.type === "light" || single?.type === "scene") where = this._entityParts(single.id).secondary;
      else if (single?.type === "device") where = [this._deviceArea(single.id), where].filter(Boolean).join(" · ");
      const excluded = this._targetItems(row.target.exclude).length;
      if (excluded) where = [where, this._t("left_out", { count: excluded })].filter(Boolean).join(" · ");
      const rowType = single?.type ?? "several";
      const track = h("div", {
        class: "grid-track track",
        onclick: (e) => this._addBar(e, row, track),
      });
      const sim = h("i", { class: "simline" });
      this._simEls.push(sim);
      track.append(...sunLines(), sim);
      for (const bar of row.bars) this._buildBar(track, row, bar);
      return h(
        "div",
        { class: "line" },
        h(
          "div",
          {
            class: `line-name${this._selectedRow === row.id ? " sel" : ""}`,
            title: members.map((m) => this._entityLabel(m.id)).join(", "),
            onclick: () => {
              this._selectedRow = row.id;
              this._selectedBar = null;
              this._renderDetail();
              this._renderTimeline();
            },
          },
          icon(ICONS.type[rowType], this._t(`type.${rowType}`)),
          h("span", {}, h("span", { class: "clamp" }, name), where ? h("small", {}, where) : null),
          h(
            "button",
            {
              "aria-label": this._t("remove", { name }),
              title: this._t("remove", { name }),
              onclick: (e) => {
                e.stopPropagation();
                this._removeRow(row);
              },
            },
            "×"
          )
        ),
        track
      );
    });
    this._linesEl.replaceChildren(
      ...(lines.length ? [axis, ...lines] : [axis, h("p", { class: "muted", style: "padding:8px 2px" }, this._t("no_rows"))])
    );
    this._syncSimulation();
    if (focused) this._barEls.get(focused)?.main.focus();
  }

  _buildBar(track, row, bar) {
    const [paint, style] = this._paint(row, bar);
    const piece = (extra) => {
      const element = h("div", {
        class: `tbar ${paint} ${extra}`.trim(),
        tabindex: extra === "wrapped" ? -1 : 0,
        role: "button",
        onpointerdown: (e) => this._dragStart(e, row, bar, element),
        onpointermove: (e) => this._dragMove(e),
        onpointerup: () => this._dragEnd(),
        onpointercancel: () => this._dragEnd(),
        onclick: () => this._tapBar(bar),
        onkeydown: (e) => this._barKey(e, row, bar),
      });
      element.dataset.bar = bar.id;
      element.dataset.paint = style;
      return element;
    };
    const main = piece("main");
    const wrap = piece("wrapped");
    const handle = (side, name) =>
      h(
        "div",
        {
          class: `handle ${side}`,
          onpointerdown: (e) => this._dragStart(e, row, bar, e.currentTarget, side),
          onpointermove: (e) => this._dragMove(e),
          onpointerup: () => this._dragEnd(),
          onpointercancel: () => this._dragEnd(),
        },
        icon(name)
      );
    const handles =
      this._selectedBar === bar.id ? { start: handle("start", "mdi:chevron-left"), end: handle("end", "mdi:chevron-right") } : null;
    this._barEls.set(bar.id, { main, wrap, row, bar, handles });
    track.append(main, wrap);
    if (handles) track.append(handles.start, handles.end);
    this._paintBar(bar);
    this._fillBar(bar);
  }

  _paintBar(bar) {
    const parts = this._barEls.get(bar.id);
    const [start, end] = this._span(bar);
    const from = this._relative(start, this._axis);
    const length = end - start;
    const fits = from + length <= DAY;
    const firstWidth = fits ? length : DAY - from;
    const selected = this._selectedBar === bar.id ? " sel" : "";
    const details = this._preview?.flows?.[this._selected]?.bars?.[bar.id];
    const dim = details && !details.length ? " dim" : "";
    const paint = this._paint(parts.row, bar)[0];
    parts.main.className = `tbar main ${paint}${selected}${dim}${fits ? "" : " wrapping"}`;
    parts.main.style.cssText = `${parts.main.dataset.paint}left:${(from / DAY) * 100}%;width:${(firstWidth / DAY) * 100}%`;
    parts.wrap.className = `tbar wrapped ${paint}${selected}${dim}`;
    parts.wrap.hidden = fits;
    parts.wrap.style.cssText = `${parts.wrap.dataset.paint}left:0;width:${((length - firstWidth) / DAY) * 100}%`;
    if (parts.handles) {
      // Beside the bar, so that even a short bar can still be grabbed in the middle.
      const edge = (minutes) => (mod(minutes, DAY) / DAY) * 100;
      const place = (left) => `left:clamp(0px, ${left}, calc(100% - ${HANDLE}px))`;
      parts.handles.start.style.cssText = place(`calc(${edge(from)}% - ${HANDLE}px)`);
      parts.handles.end.style.cssText = place(`${edge(from + length)}%`);
    }
    const title = `${this._startText(bar.start)} – ${this._endText(bar.end)}${dim ? `. ${this._t("not_this_day", { day: this._dayNames[this._pvDay] })}` : ""}`;
    parts.main.title = title;
    parts.wrap.title = title;
    parts.main.setAttribute("aria-label", `${this._targetText(parts.row)}: ${title}`);
  }

  _fillBar(bar) {
    const { main, wrap, row } = this._barEls.get(bar.id);
    const [start, end] = this._span(bar);
    const length = end - start;
    const scene = this._onlyScenes(row);
    const action =
      bar.look.mode === "off" || bar.look.mode === "unchanged"
        ? ICONS.look[bar.look.mode]
        : ICONS.at_start[bar.at_start];
    const label = scene ? this._t("scene_bar") : this._lookLabel(bar.look);
    const content = [
      length >= 40 ? icon(ICONS.start[bar.start.type]) : null,
      length >= 90 && !scene ? icon(action) : null,
      length >= 180 ? h("span", { class: "txt" }, label) : null,
      h("span", { class: "spacer" }),
      length >= 150 && bar.look.mode !== "unchanged" && ICONS.at_end[bar.at_end] ? icon(ICONS.at_end[bar.at_end]) : null,
      length >= 120 && bar.end.type !== "time" ? icon(ICONS.start[bar.end.type]) : null,
    ].filter(Boolean);
    const grips = () => [h("i", { class: "grip l" }), h("i", { class: "grip r" })];
    main.replaceChildren(...grips(), ...content);
    wrap.replaceChildren(...grips());
  }

  _addBar(event, row, track) {
    if (event.target.closest(".tbar, .handle")) return;
    if (this._selectedBar && isTouch()) {
      this._selectBar(null);
      return;
    }
    const box = track.getBoundingClientRect();
    const start = snap(((event.clientX - box.left) / box.width) * DAY + this._axis * 60);
    const others = this._others(row, null);
    let limit = start + 60;
    for (const [from] of others) {
      for (const shifted of [from - DAY, from, from + DAY]) {
        if (shifted >= start && shifted < limit) limit = shifted;
      }
    }
    if (limit - start < SHORTEST) return;
    const scene = this._onlyScenes(row);
    const bar = {
      id: randomId(),
      start: { type: "time", time: toClock(start), elevation: null, offset: 0 },
      end: { type: "time", time: toClock(limit), offset: 0 },
      at_start: "turn_on",
      at_end: "turn_off",
      look: scene ? { ...newLook(), mode: "keep", brightness: null } : newLook(),
    };
    row.bars.push(bar);
    this._selectedBar = bar.id;
    this._renderDetail();
    this._changed();
  }

  _others(row, bar) {
    return row.bars.filter((other) => other !== bar).map((other) => this._span(other));
  }

  // Dragging: a bar stays between its neighbours; sun edges keep their sun and change the offset.

  _limits(row, bar, start, end) {
    let low = -Infinity;
    let high = Infinity;
    for (const [from, to] of this._others(row, bar)) {
      for (const shift of [-DAY, 0, DAY]) {
        if (to + shift <= start) low = Math.max(low, to + shift);
        if (from + shift >= end) high = Math.min(high, from + shift);
      }
    }
    return [low, high];
  }

  _selectBar(id) {
    this._selectedBar = id;
    this._renderDetail();
    this._renderTimeline();
  }

  // By touch the first tap only selects, so that a swipe over a bar still scrolls the page.
  _tapBar(bar) {
    if (this._selectedBar !== bar.id) this._selectBar(bar.id);
  }

  _dragStart(event, row, bar, element, side = null) {
    if (event.button !== 0 && event.pointerType === "mouse") return;
    if (!side && event.pointerType !== "mouse" && this._selectedBar !== bar.id) return;
    event.preventDefault();
    event.stopPropagation();
    element.focus({ preventScroll: true });
    const grip = event.target.closest?.(".grip");
    const mode = side ?? (grip ? (grip.classList.contains("l") ? "start" : "end") : "move");
    const [start, end] = this._span(bar);
    this._drag = {
      row,
      bar,
      mode,
      x: event.clientX,
      width: element.parentElement.getBoundingClientRect().width,
      start,
      end,
      limits: this._limits(row, bar, start, end),
      moved: false,
    };
    element.setPointerCapture(event.pointerId);
  }

  _shift(drag, minutes) {
    const { bar, mode, start, end } = drag;
    const [low, high] = drag.limits;
    const length = end - start;
    if (mode === "move") {
      const moved = Math.max(low, Math.min(high - length, snap(start + minutes)));
      this._setAnchor(bar.start, moved, true);
      this._setAnchor(bar.end, moved + length, false);
    } else if (mode === "start") {
      const lowest = Math.max(low, end - DAY + SNAP);
      this._setAnchor(bar.start, Math.max(lowest, Math.min(end - SHORTEST, snap(start + minutes))), true);
    } else {
      const highest = Math.min(high, start + DAY - SNAP);
      this._setAnchor(bar.end, Math.max(start + SHORTEST, Math.min(highest, snap(end + minutes))), false);
    }
  }

  _dragMove(event) {
    const drag = this._drag;
    if (!drag) return;
    if (!drag.moved) {
      if (Math.abs(event.clientX - drag.x) < (event.pointerType === "mouse" ? 4 : 8)) return;
      drag.moved = true;
      drag.x = event.clientX;
    }
    this._shift(drag, ((event.clientX - drag.x) / drag.width) * DAY);
    this._paintBar(drag.bar);
    this._showBubble(event, drag.bar);
  }

  _showBubble(event, bar) {
    if (!this._bubble) {
      this._bubble = h("div", { class: "bubble" });
      this.shadowRoot.append(this._bubble);
    }
    this._bubble.textContent = `${this._startText(bar.start)} – ${this._endText(bar.end)}`;
    this._bubble.style.left = `${event.clientX}px`;
    this._bubble.style.top = `${event.clientY}px`;
  }

  _dragEnd() {
    const drag = this._drag;
    if (!drag) return;
    this._drag = null;
    this._bubble?.remove();
    this._bubble = null;
    this._selectedBar = drag.bar.id;
    this._renderDetail();
    if (drag.moved) this._changed();
    else this._renderTimeline();
  }

  _barKey(event, row, bar) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      this._selectedBar = bar.id;
      this._renderDetail();
      this._renderTimeline();
      return;
    }
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    const [start, end] = this._span(bar);
    const step = (event.key === "ArrowLeft" ? -1 : 1) * (event.shiftKey ? 30 : SNAP);
    const drag = { bar, mode: "move", start, end, limits: this._limits(row, bar, start, end) };
    this._shift(drag, step);
    this._selectedBar = bar.id;
    this._renderDetail();
    this._changed();
  }

  // Selected bar

  _renderDetail() {
    if (!this._detailEl) return;
    const found = this._selectedBar ? this._findBar(this._selectedBar) : null;
    const row = found?.row ?? this._current?.rows.find((r) => r.id === this._selectedRow);
    if (!row) {
      this._detailEl.replaceChildren(h("p", { class: "hint" }, this._t("select_bar")));
      return;
    }
    this._selectedRow = row.id;
    const rowSection = this._rowSection(row);
    if (!found) {
      this._detailEl.replaceChildren(...rowSection, h("p", { class: "hint" }, this._t("select_bar")));
      return;
    }
    const { bar } = found;
    const scene = this._onlyScenes(row);
    const redraw = () => {
      this._renderDetail();
      this._changed();
    };
    this._detailEl.replaceChildren(
      ...rowSection,
      h("div", { class: "sec" }, this._t("selected", { who: this._targetText(row) })),
      h(
        "div",
        { class: "grid" },
        this._startFields(bar, redraw),
        this._endFields(bar, redraw),
        this._actionFields(bar, scene, redraw)
      ),
      ...(scene
        ? [h("p", { class: "hint" }, this._t("scene_activates"))]
        : [h("div", { class: "sec" }, this._t("look")), this._lookEditor(bar)]),
      h(
        "div",
        { class: "inline" },
        h(
          "button",
          {
            class: "danger",
            onclick: () => {
              row.bars.splice(row.bars.indexOf(bar), 1);
              this._selectedBar = null;
              redraw();
            },
          },
          this._t("remove_bar")
        )
      )
    );
  }

  _rowSection(row) {
    const title = h("div", { class: "sec" }, this._t("row_section"));
    if (!customElements.get("ha-selector")) return [title, h("p", { class: "hint" }, this._targetText(row))];
    return [
      title,
      this._targetPicker(row.target, (target, picker) => {
        row.target = target;
        picker.value = target;
        this._changed();
      }),
    ];
  }

  _clockInput(value, onchange) {
    return h("input", {
      type: "time",
      value: value ?? "",
      onchange: (e) => {
        onchange(e.target.value || null);
        this._changed();
      },
    });
  }

  _offsetField(anchor) {
    return h(
      "label",
      { class: "fld" },
      this._t("offset"),
      h("input", {
        type: "number",
        min: -720,
        max: 720,
        step: SNAP,
        value: anchor.offset ?? 0,
        onchange: (e) => {
          anchor.offset = Math.max(-720, Math.min(720, Math.round(Number(e.target.value) || 0)));
          this._changed();
        },
      })
    );
  }

  _startFields(bar, redraw) {
    const { start } = bar;
    const fields = [
      this._select_(
        this._fieldLabel(ICONS.start[start.type], this._t("starts")),
        start.type,
        this._options_("start", ["time", "sunset", "sunrise", "sun_elevation"]),
        (value) => {
          const at = this._span(bar)[0];
          start.type = value;
          start.offset = 0;
          start.time = value === "time" ? toClock(at) : null;
          if (value === "sun_elevation" && start.elevation === null) start.elevation = 12;
          redraw();
        }
      ),
    ];
    if (start.type === "sun_elevation") {
      fields.push(
        h(
          "label",
          { class: "fld" },
          this._t("sun_below"),
          h("input", {
            type: "number",
            min: -20,
            max: 80,
            step: 0.5,
            value: start.elevation ?? "",
            onchange: (e) => {
              start.elevation = e.target.value === "" ? null : Number(e.target.value);
              this._changed();
            },
          })
        )
      );
    } else if (start.type !== "time") {
      fields.push(this._offsetField(start));
    }
    fields.push(
      h(
        "label",
        { class: "fld" },
        this._t(start.type === "time" ? "time" : "not_before"),
        this._clockInput(start.time, (value) => (start.time = value))
      )
    );
    return fields;
  }

  _endFields(bar, redraw) {
    const { end } = bar;
    return [
      this._select_(
        this._fieldLabel(ICONS.start[end.type], this._t("ends")),
        end.type,
        this._options_("end", ["time", "sunset", "sunrise"]),
        (value) => {
          const at = this._span(bar)[1];
          end.type = value;
          end.offset = 0;
          end.time = value === "time" ? toClock(at) : null;
          redraw();
        }
      ),
      end.type === "time"
        ? h("label", { class: "fld" }, this._t("time"), this._clockInput(end.time, (value) => (end.time = value)))
        : this._offsetField(end),
    ];
  }

  _actionFields(bar, scene, redraw) {
    const fields = [];
    const set = (key) => (value) => {
      bar[key] = value;
      redraw();
    };
    const lookDecides = bar.look.mode !== "off" && bar.look.mode !== "unchanged";
    if (!scene && lookDecides) {
      fields.push(
        this._select_(
          this._fieldLabel(ICONS.at_start[bar.at_start], this._t("at_start")),
          bar.at_start,
          this._options_("at_start", ["turn_on", "adjust"]),
          set("at_start")
        )
      );
    }
    if (bar.look.mode !== "unchanged") {
      fields.push(
        this._select_(
          ICONS.at_end[bar.at_end] ? this._fieldLabel(ICONS.at_end[bar.at_end], this._t("at_end")) : this._t("at_end"),
          bar.at_end,
          this._options_("at_end", ["turn_off", "restore", "nothing"]),
          set("at_end")
        )
      );
    }
    return fields;
  }

  _lookEditor(bar) {
    const look = bar.look;
    const body = h("div", { class: "look" });
    const draw = () => {
      const children = [this._lookModes(look)];
      if (look.mode !== "off" && look.mode !== "unchanged") {
        if (look.mode !== "keep") children.push(this._swatches(look, draw));
        if (look.mode === "white") children.push(this._temperatureField(look));
        if (look.mode === "color") children.push(this._colorWheel(look));
        children.push(...this._brightnessFields(look, draw));
      }
      body.replaceChildren(...children);
    };
    draw();
    return body;
  }

  _lookModes(look) {
    return h(
      "div",
      { class: "modes" },
      ["keep", "white", "color", "off", "unchanged"].map((mode) =>
        h(
          "button",
          {
            "aria-pressed": String(look.mode === mode),
            onclick: () => {
              look.mode = mode;
              this._renderDetail();
              this._changed();
            },
          },
          this._t(`look_mode.${mode}`)
        )
      )
    );
  }

  _swatches(look, draw) {
    return h(
      "div",
      { class: "swatches" },
      PRESETS.map(([key, preset]) => {
        const [background] = lookColors({ ...newLook(), ...preset });
        return h("button", {
          "aria-label": this._t(key),
          title: this._t(key),
          style: `background:${background}`,
          onclick: () => {
            Object.assign(look, preset);
            draw();
            this._changed();
          },
        });
      })
    );
  }

  _temperatureField(look) {
    const value = h("span", {}, `${look.kelvin} K`);
    const setKelvin = (kelvin) => {
      look.kelvin = kelvin;
      value.textContent = `${kelvin} K`;
      this._changed();
    };
    const clamped = Math.min(6500, Math.max(2000, look.kelvin));
    let slider;
    if (customElements.get("ha-selector")) {
      slider = document.createElement("ha-selector");
      slider.hass = this._hass;
      slider.selector = { color_temp: { unit: "kelvin", min: 2000, max: 6500 } };
      slider.value = clamped;
      slider.addEventListener("value-changed", (e) => setKelvin(Number(e.detail.value)));
    } else {
      slider = h("input", {
        type: "range",
        min: 2000,
        max: 6500,
        step: 50,
        value: clamped,
        oninput: (e) => setKelvin(Number(e.target.value)),
      });
    }
    return h("div", { class: "fld" }, h("span", {}, `${this._t("temperature")} `, value), slider);
  }

  _brightnessFields(look, draw) {
    const fields = [
      h(
        "label",
        { class: "check" },
        h("input", {
          type: "checkbox",
          checked: look.brightness !== null,
          onchange: (e) => {
            look.brightness = e.target.checked ? 80 : null;
            draw();
            this._changed();
          },
        }),
        this._t("set_brightness")
      ),
    ];
    if (look.brightness === null) return fields;
    const percent = h("span", {}, `${look.brightness}%`);
    fields.push(
      h(
        "label",
        { class: "fld" },
        h("span", {}, `${this._t("brightness")} `, percent),
        h("input", {
          type: "range",
          min: 1,
          max: 100,
          step: 1,
          value: look.brightness,
          oninput: (e) => {
            look.brightness = Number(e.target.value);
            percent.textContent = `${look.brightness}%`;
            this._changed();
          },
        })
      )
    );
    return fields;
  }

  _colorWheel(look) {
    const dot = h("i");
    const set = (hue, saturation) => {
      look.rgb = hsToRgb(hue, saturation);
      place();
      this._changed();
    };
    const pick = (event) => {
      const box = wheel.getBoundingClientRect();
      const x = ((event.clientX - box.left) / box.width) * 2 - 1;
      const y = ((event.clientY - box.top) / box.height) * 2 - 1;
      set(mod((Math.atan2(y, x) * 180) / Math.PI, 360), Math.min(1, Math.hypot(x, y)));
    };
    const wheel = h(
      "div",
      {
        class: "wheel",
        tabindex: 0,
        role: "slider",
        "aria-label": this._t("color"),
        onpointerdown: (e) => {
          wheel.setPointerCapture(e.pointerId);
          pick(e);
        },
        onpointermove: (e) => {
          if (wheel.hasPointerCapture(e.pointerId)) pick(e);
        },
        onkeydown: (e) => {
          const [hue, saturation] = rgbToHs(look.rgb);
          const turn = { ArrowLeft: -5, ArrowRight: 5 }[e.key] ?? 0;
          const fade = { ArrowDown: -0.05, ArrowUp: 0.05 }[e.key] ?? 0;
          if (!turn && !fade) return;
          e.preventDefault();
          set(mod(hue + turn, 360), Math.max(0, Math.min(1, saturation + fade)));
        },
      },
      dot
    );
    const place = () => {
      const [hue, saturation] = rgbToHs(look.rgb);
      const angle = (hue * Math.PI) / 180;
      const left = 50 + 50 * saturation * Math.cos(angle);
      const top = 50 + 50 * saturation * Math.sin(angle);
      dot.style.cssText = `left:${left}%;top:${top}%;background:rgb(${look.rgb.join(",")})`;
    };
    place();
    return wheel;
  }

  // Arrival preview

  _buildPreviewControls() {
    this._previewResult = h("div");
    this._pvTimeInput = h("input", {
      type: "time",
      value: this._pvTime,
      onchange: (e) => {
        if (!e.target.value) return;
        this._pvTime = e.target.value;
        this._syncSimulation();
        this._requestPreview();
      },
    });
    this._pvSlider = h("input", {
      type: "range",
      class: "sim-slider",
      min: 0,
      max: DAY - 1,
      step: 1,
      "aria-label": this._t("at"),
      oninput: (e) => {
        this._pvTime = toClock(Number(e.target.value));
        this._pvTimeInput.value = this._pvTime;
        this._syncSimulation(true);
        this._requestPreview();
      },
    });
    this._pvDayButtons = this._dayNames.map((name, index) =>
      h("button", { type: "button", onclick: () => this._setSimulation(index, this._pvTime) }, name)
    );
    this._previewEl.replaceChildren(
      h("div", { class: "sec", style: "margin-top:0" }, this._t("simulation")),
      h(
        "div",
        { class: "sim-head" },
        h("div", { class: "fld" }, this._t("day"), h("div", { class: "days" }, this._pvDayButtons)),
        h(
          "div",
          { class: "sim-time" },
          h("label", { class: "fld" }, this._t("time"), this._pvTimeInput),
          h(
            "button",
            {
              type: "button",
              onclick: () => {
                const now = new Date();
                this._setSimulation((now.getDay() + 6) % 7, clockOf(now));
              },
            },
            this._t("now")
          )
        )
      ),
      this._pvSlider,
      this._previewResult
    );
    this._syncSimulation();
  }

  _setSimulation(day, time) {
    this._pvDay = day;
    this._pvTime = time;
    this._pvTimeInput.value = time;
    this._syncSimulation();
    this._renderFlows();
    this._requestPreview();
  }

  _syncSimulation(fromSlider = false) {
    const minutes = toMinutes(this._pvTime);
    const position = this._relative(minutes, this._axis ?? 0);
    if (!fromSlider && this._pvSlider) this._pvSlider.value = minutes;
    this._pvSlider?.style.setProperty("--pos", `${(minutes / DAY) * 100}%`);
    this._pvDayButtons?.forEach((button, index) => button.setAttribute("aria-pressed", String(index === this._pvDay)));
    for (const line of this._simEls ?? []) {
      line.style.left = `${(position / DAY) * 100}%`;
    }
  }

  _renderPreviewResult() {
    const result = this._preview;
    if (!result) return;
    if (!result.lights.length && !result.scenes.length) {
      this._previewResult.replaceChildren(h("p", { class: "muted" }, this._t("no_lights")));
      return;
    }
    const tiles = result.lights.map((light) => {
      const { action } = light;
      const off = action?.kind === "off";
      let tint = "var(--secondary-text-color)";
      if (action && !off) tint = action.mode === "keep" ? "var(--state-light-active-color, var(--primary-color))" : lookColors(action)[0];
      const { primary, secondary } = this._entityParts(light.id);
      let state = this._t("unchanged");
      if (action) state = `${off ? this._t("off") : this._lookLabel(action)} · ${light.flow.trim() || this._t("unnamed")}`;
      return h(
        "div",
        { class: "sim-tile" },
        h(
          "span",
          { class: "sim-badge", style: `--tint:${tint}` },
          icon(off ? "mdi:lightbulb-off-outline" : action ? "mdi:lightbulb-on" : "mdi:lightbulb-outline")
        ),
        h(
          "span",
          { class: "sim-text" },
          h("span", {}, primary),
          secondary ? h("small", {}, secondary) : null,
          h("small", {}, state)
        )
      );
    });
    const children = [h("div", { class: "sim-tiles" }, tiles)];
    if (result.scenes.length) {
      const scenes = this._list(result.scenes.map((s) => this._entityLabel(s.id)));
      children.push(h("p", { class: "muted" }, this._t("also_activated", { scenes })));
    }
    this._previewResult.replaceChildren(...children);
  }
}

if (!customElements.get("light-planner-panel")) {
  customElements.define("light-planner-panel", LightPlannerPanel);
}
