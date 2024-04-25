from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
import time
from datetime import datetime
import os

# enable the headless mode
options = Options()

# initialize a web driver to control Chrome
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()),
    options=options
)

# maxime the controlled browser window
driver.fullscreen_window()

# the URL of the target page to scrape
url = 'https://www.reddit.com/r/gaming/'
# connect to the target URL in Selenium
driver.get(url)

# essaie de rajout d'une validation du cookie 18+ pour les comptes nsfw mais ne marche pas
# driver.add_cookie({'name': 'over18', 'value': '1'})

# sleep(500)

# initialize the dictionary that will contain
# the subreddit scraped data
subreddit_data = []
utilisateurs_recuperes = []

# nom du subreddit
name = driver.find_element(By.CSS_SELECTOR, '.font-bold.text-18')

# description du ssubreddit (ne ser à rien dans notre cas)
# description = driver.find_element(By.CSS_SELECTOR, '.xs\\:hidden.text-left.text-\\[12px\\].text-neutral-content-strong')

distance_defilement = 700  # Distance de défilement à chaque itération
nb_defilement = 10  # Nombre de défilements à effectuer

# Effectuez le défilement pour charger les utilisateurs
for i in range(0, nb_defilement):
    # Défilement vers le bas
    driver.execute_script("window.scrollBy(0, " + str(distance_defilement) + ");")
    sleep(2)  # Attend quelques secondes pour le chargement

# Récupération des utilisateurs
utilisateurs_visibles = driver.find_elements(By.CSS_SELECTOR, 'span.whitespace-nowrap')

# Ajoutez les utilisateurs visibles à la liste
utilisateurs_recuperes.extend([utilisateur.text for utilisateur in utilisateurs_visibles])
utilisateurs_recuperes = list(set(utilisateurs_recuperes))

while '• Officiel' in utilisateurs_recuperes:
    utilisateurs_recuperes.remove('• Officiel')

# add the scraped data to the dictionary
subreddit_data.append({
    'Name': name.text,
    'Users': utilisateurs_recuperes
})

# print(subreddit_data)


# Créez un DataFrame à partir des données du subreddit
df = pd.DataFrame(subreddit_data)

# Créez un nouveau DataFrame avec chaque utilisateur dans une ligne séparée
df_users = pd.DataFrame(df['Users'].values[0], columns=['Users'])

# Ajoutez le nom du subreddit comme colonne au début du DataFrame
df_users.insert(0, 'Subreddit', df['Name'].values[0])

# Enregistrez le DataFrame dans un fichier CSV
csv_filename = 'subreddit_data_test.csv'
df_users.to_csv(csv_filename, index=False)

liste_subreddit = []
subreddit_data2 = []

for index, row in df_users.iterrows():
    subreddit_user = row['Subreddit']
    url2 = "https://www.reddit.com/user/"+row['Users'][2:]
    driver.get(url2)
    # driver.add_cookie({'name': 'over18', 'value': '1'})

    liste_subreddit.clear()
    subreddit_data2.clear()

    for i in range(0, nb_defilement):
        # Défilement vers le bas
        driver.execute_script("window.scrollBy(0, " + str(distance_defilement) + ");")
        sleep(2)  # Attend quelques secondes pour le chargement

    subreddit_visibles = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="location-anchor"]')

    for element_a in subreddit_visibles:
        # Récupérer le texte à l'intérieur de l'élément <span>
        if element_a.text:
            if (element_a.text not in liste_subreddit) and (element_a.text != subreddit_user):
                liste_subreddit.append(element_a.text)
                print(element_a.text)

    subreddit_data2.append({
        'Source': subreddit_user,
        'Target': liste_subreddit
    })

    # print(subreddit_data2)

    df2 = pd.DataFrame(subreddit_data2)
    df2.to_csv('test2.csv', index=False)

    # Créez un nouveau DataFrame avec chaque utilisateur dans une ligne séparée
    df_sub = pd.DataFrame(df2['Target'].values[0], columns=['Target'])

    # Ajoutez le nom du subreddit comme colonne au début du DataFrame
    df_sub.insert(0, 'Source', df2['Source'].values[0])

    # Enregistrez le DataFrame dans un fichier CSV
    csv_filename = 'test_edges.csv'
    if os.path.exists(csv_filename):
        df_sub.to_csv(csv_filename, mode='a', header=False, index=False)
    else:
        df_sub.to_csv(csv_filename, index=False)

# Fermez le navigateur web
driver.quit()