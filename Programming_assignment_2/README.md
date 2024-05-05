# Programming_assignment_2

## Startup

- Install Selenium: `pip install selenium` 
- Install xmlx: `pip install lxml` 

V 26. vrstici je potrebno nastaviti lokacijo za firefox, ki se uporablja za selenium, ampak ta del je potreben le ko smo 
renderirali spletne strani, ki so shranjene v svojih posameznih mapah. Take strani so označene z dvema podčrtajema spredaj npr: `input-extraction/overstock.com/__jewlery01.html`

## Running

Za to da zaženemo program je potrebno v cmd-ju `python run-extraction.py #`, kjer # zamenjamo z implementacijo, ki jo želimo uporabiti za ekstrakcijo.
- Za RegEx ekstrakcijo vpišemo A - `python run-extraction.py A`
- Za XPath ekstrakcijo vpišemo B - `python run-extraction.py B`
- Za RoadRunner ekstrakcijo vpišemo C - `python run-extraction.py C`