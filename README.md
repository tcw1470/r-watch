# Refugee-Watch

## About

- The source code of this app can be found on [GitHub](https://github.com/tcw1470/r-watch/)
- [TL;DR](https://docs.google.com/document/d/1Bfnug4c1sEtNNPn9orecEp7OObfDtn2wWqfM5nM8Rws/)


## Usage notes on select pages

<details>

<summary>Fit Prophet </summary>

1) Users are required to first fetch data from Climate Serv
2) Users may then click to train and fit a Prophet model

</details> 


<details>

<summary>Fit a deep Auto-Regressive model </summary>

1) Users are required to enter a string describing a place
2) Users then explicitly click start to fetch data from ClimateServ 
3) Users may then click to train and fit a DeepAR model

</details> 


## Repo's file structure

```
.
├── src/
│   ├── requirements.txt
│   ├── utils.py
│   ├── Home.py  # rendered
│   └── pages  /
│       ├── Fit_deepAR.py 
│       ├── Fit_prophet.py
│       ├── More_stats.py
│       └── ...
└── data/
    └── Gaza /
        └── ...
```        
Revise the source of above tree diagram [here](https://tree.nathanfriend.com/?s=(%27options!(%27fancy2~fullPath!false~trailingSlash2~rootDot2)~3(%273%27src*requirements.txt*utils0**Home0-%23%20rendered*pages-5deepAR0%205prophet04More_stats0746data*Gaza%207*%27)~version!%271%27)*6--%20%200.py2!true3source!4*-54Fit_6%5Cn74...%017654320-*)


