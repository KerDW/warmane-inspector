import PySimpleGUI as sg
import asyncio
from pyppeteer import launch
import os

async def screenshotSpecs(name):
    browser = await launch()
    page = await browser.newPage()

    try:
        await page.goto('https://armory.warmane.com/character/'+name+'/Lordaeron/talents')
        # focus page to avoid tooltips
        await page.bringToFront()

        # change spec through js click (if currently in OS it'll error)
        await page.click('#character-sheet > table > tbody > tr > td:nth-child(1) > a')

        # get mainspec and save screenshot
        await page.waitForSelector('#spec-0')
        element = await page.querySelector('#spec-0')  
        await element.screenshot({'path': 'talents0.png'})

        # change spec through js click
        await page.click('#character-sheet > table > tbody > tr > td:nth-child(3) > a')

        # screenshot offspec
        await page.waitForSelector('#spec-1')
        element = await page.querySelector('#spec-1')
        await element.screenshot({'path': 'talents1.png'})

        return 1
    except:
        await browser.close()
        return 0

def newWindow(window):
    while True:
        event, values = window.read()
        if event == "OK" or event == sg.WIN_CLOSED:
            break
    window.close()

# asyncio.get_event_loop().run_until_complete(screenshotSpecs())

base_layout = [  
            [sg.Text('Character name:'), sg.InputText(), sg.Button('Inspect')]
         ]

print(os. getcwd())

popup_success = [
    [sg.Image(os.getcwd()+'\\'+'talents0.png'), sg.Image(os.getcwd()+'\\'+'talents1.png')]
]

popup_fail = [
    [sg.Text("Couldn't find the character")],
    [sg.Button('OK')]
]  

window = sg.Window('Warmane inspector', base_layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if asyncio.get_event_loop().run_until_complete(screenshotSpecs(values[0])) == True:
        window2 = sg.Window('Character info', popup_success)
        newWindow(window2)
    else:
        window3 = sg.Window('Character info', popup_fail)
        newWindow(window3)

window.close()