# RSSRadar Backend

## Aperçu

RssRadar est un moteur de recherche basé sur des flux RSS. Ce dépôt contient le projet backend développé avec Python, permettant aux utilisateurs de rechercher des articles et des informations à partir de flux RSS. Il y a une api avec différentes routes spécifiées dans la documentation openAPI. L'application se sépare en deux micro services, d'un côté l'api et de l'autre le worker.

Le worker, à partir d'une liste de flux initiaux va chercher des articles ainsi que de nouveaux flux présents dans ces articles afin d'aggrandir la quantitée de données dans la base.

Ce projet backend est complété par un frontend qui permet d'intéragir avec l'api.

## Fonctionnalités

- Websub hub
- Recherche
- Crawling
- Exploring
- Indexing

Notre Crawler est récurssif, c'est à dire qu'il va récupérer les liens des articles dans les flux RSS, accéder à la page web de l'article et chercher les attributs 'href' des balises <link> avec comme attribut 'type'='application/rss+xml'. Ces nouveau liens sont ajoutés ensuite à la DB pour qu'une fois le crawler soit relancé, ces nouveaux liens soient crawlés.

Pour lancer le crawler, on éxécute app.py, qui appelera scheduler.py afin de pouvoir crawler tous les liens RSS toutes les 30 minutes.

## Utilisation du websub hub

1 - Subscribtion

Le client doit faire une requête POST sur la route `/websub` de l'api. Il doit fournir au minimum un hub.mode à subscribe, hub.topic (url du feed auquel on veut s'abonner) et un hub.callback qui doit correspondre à l'url où on envoiera les nouveaux items lorsqu'il y en a. Il peut également spécifier un hub.secret permettant de vérifier si le serveur qui envoie les données est bien celui auquel on s'est abonné. Également, la durée de l'abonnement peut être spécifié (hub.lease_seconds) et il est fixé par défaut à 3600000s.

Une fois le POST effectué, un GET s'effectue sur le client afin de confirmer l'url de callback avec un challenge.

2 - Notify

Notre application étant composée d'un crawler, l'objectif est de notifier les clients websub lorsqu'il y a de nouveaux items sur un flux sur lequel ils se sont abonnés. Les clients seront donc notifiés sur l'url de callback spécifiée lorsque le besoin est.

3 - Unsubscribe

Pour se désabonner, le client peut faire un POST sur la route `/websub` de l'api avec hub.mode à unsubscribe.

## Dépôts

- [RssRadar Frontend](https://github.com/Projet-agile-FILA1-G3/frontend) : Dépôt du frontend qui permet d'intéragir avec notre moteur de recherche

## Auteurs

Ce projet a été développé par :

- Zineddine CHALEKH - zineddine.chalekh@imt-atlantique.net
- Frédéric EGENSCHEVILLER - frederic.egenscheviller@imt-atlantique.net
- Elias MORIO - elias.morio@imt-atlantique.net
- Ruben SAILLY - ruben.sailly@imt-atlantique.net

---

Merci d'utiliser RssRadar ! Si vous avez des questions ou des suggestions, n'hésitez pas à nous contacter.
