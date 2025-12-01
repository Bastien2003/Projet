import pooch
import pandas as pd

def load_all_data():
    urls = {
    "albi_intercites": "https://drive.google.com/uc?export=download&id=1sOx07CWnSI4uF-EbekytHxp7pM-efv1T",
    "bayonne_intercites" : "https://drive.google.com/uc?export=download&id=1NmcPWkFA0oyWByA0qzFfDCmeAwGK26-W",
    "beziers_intercites" : "https://drive.google.com/uc?export=download&id=1UWqKtoOyDCjLX1VJ6ZmAW-wIMXGkL-y7",
    "latour_de_carol_intercites" : "https://drive.google.com/uc?export=download&id=1foFmCtiKbj9B6lq0ILwNQ6ZCa984LBqV",
    "liste_des_gares" : "https://drive.google.com/uc?export=download&id=1Ykru6rmhBiL2X6w8x2DN_O8e2T75hbPs",
    "liste_gares_occitanie" : "https://drive.google.com/uc?export=download&id=1AcqdNzwO6k7Q5pH0gB1aoU63-D-QA2a0",
    "montpellier_tgv" : "https://drive.google.com/uc?export=download&id=1FiJxM43xx25_LXExDXkDieBViMwmrRN7",
    "nimes_intecites" : "https://drive.google.com/uc?export=download&id=1U-bejnzcD0pcff57-j0sA4bw-0VX4g75",
    "nimes_tgv" : "https://drive.google.com/uc?export=download&id=1DTDlzaO5dsXJa8dpaDfYJ2YfZlS5VoWH",
    "perpigan_tgv" : "https://drive.google.com/uc?export=download&id=11hzTpFsX2UnF0X1Sm9j8YzRa_PJyF6V2",
    "tarbes_intercites" :"https://drive.google.com/uc?export=download&id=17LmGs782zTpTnC7jw4eQoEQ-QnUipyMI",
    "toulouse_intercites" : "https://drive.google.com/uc?export=download&id=1sL1GmwBQwLXLQGpnRXg5vwJZ4AjC7cMn",
    "toulouse_tgv" : "https://drive.google.com/uc?export=download&id=14mtGuOHL9T5S5DTch7wnKAOAMkPj6k5F",
    "cerbere_intercites" : "https://drive.google.com/uc?export=download&id=17aNXrns0-ncTSs1BZ6EGYUy3TIZJD7Jd",
    }
    
    data_dict = {}
    for name, url in urls.items():
        filename = pooch.retrieve(url=url, known_hash=None)
        data_dict[name] = pd.read_csv(filename)
    
    return data_dict
