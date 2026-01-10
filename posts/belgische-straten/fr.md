Chez moi il y a une rue avec un nom assez long: "Tweekleinewegenstraat" (Rue des deux petits chemins).
À part que quelqu'un n’a pas été capable de décider si c'était une rue ou deux (petits) chemins, je me suis plusieurs fois demandé si ça n'était pas le nom de rue le plus long de Belgique.
Heureusement répondre cette question est plutôt facile aujourd'hui, et en bidouillant avec Python et [OpenStreetMap](https://www.openstreetmap.org) on a la réponse (et plus encore)!

Le code que j'ai utilisé pour cet article se trouve [ici](/files/street-names). 

La rue dans mon quartier, avec ses pauvres 21 caractères, n'est même pas proche du top 10:

<table>
  <thead>
  <tr>
    <th>Longueur</th>
    <th>Rue</th>
    <th>Place</th>
    <th>Province<sup>1</sup></th>
  </tr>
  </thead>
  <tbody>
  <tr>
    <td>56</td>
    <td>Allée Adrienne Gommers & Anne-Marie van Oost-de-Gerlache</td>
    <td>Woluwe-Saint-Lambert</td>
    <td>Bruxelles</td>
  </tr>
  <tr>
    <td>45</td>
    <td>Rue de l'Institut Notre-Dame de la Compassion</td>
    <td>La Louvière</td>
    <td>Hainaut</td>
  </tr>
  <tr>
    <td>44 (50)</td>
    <td>Rue de la 7e Division d'Infanterie Française</td>
    <td>Ethe</td>
    <td>Luxembourg</td>
  </tr>
  <tr>
    <td>44</td>
    <td>Burgemeester Charles Rotsart de Hertainglaan</td>
    <td>Maldegem</td>
    <td>Flandre-Orientale</td>
  </tr>
  <tr>
    <td>44</td>
    <td>Burgemeester Karel Lodewijk Verbraekenstraat</td>
    <td>Sint-Gillis-Waas</td>
    <td>Flandre-Orientale</td>
  </tr>
  <tr>
    <td>43 (58)</td>
    <td>Rue du 127e Régiment d'Infanterie Française</td>
    <td>Couvin</td>
    <td>Namur</td>
  </tr>
  <tr>
    <td>43 (53)</td>
    <td>Rue du 113e Régiment d'Infanterie Française</td>
    <td>Musson</td>
    <td>Luxembourg</td>
  </tr>
  <tr>
    <td>43</td>
    <td>Rue Baron Ferdinand de Bernard de Fauconval</td>
    <td>Soignies</td>
    <td>Hainaut</td>
  </tr>
  <tr>
    <td>43</td>
    <td>Burgemeester Charles Van Cauwenberghestraat</td>
    <td>Merelbeke-Melle</td>
    <td>Flandre-Orientale</td>
  </tr>
  <tr>
    <td>42 (46)</td>
    <td>Rue du 1er Régiment des Chasseurs à Cheval</td>
    <td>Tournai</td>
    <td>Hainaut</td>
  </tr>
  <tr>
    <td>42</td>
    <td>Albert en Marie-Louise Servais-Kinetstraat</td>
    <td>Woluwe-Saint-Lambert</td>
    <td>Bruxelles</td>
  </tr>
  </tbody>
</table>

_<sup>1</sup>Je sais que Bruxelles n'est pas une province mais comme ça le tableau reste plus simple!_

## Allée Adrienne Gommers & Anne-Marie van Oost-de-Gerlache
Même si on ne compte pas les espaces, ça fait encore 50 caractères, et ça reste quand même le plus long nom de rue. L'équivalent néerlandais est plus court d’un caractère, mais seulement parce qu'il n'y a pas d'espace devant '_dreef_': **Adrienne Gommers & Anne-Marie van Oost-de Gerlachedreef**.

Celle-ci [était inaugurée](https://www.listedubourgmestre-wsl.be/inauguration-de-lallee-adrienne-gommers-anne-marie-van-oost-de-gerlache/) seulement en 2023 et est, crois-le ou non, nommée d'après Adrienne Gommers et Anne-Marie van Oost-De-Gerlache, 2 femmes de la résistance.
Autre fait intéressant: Anne-Marie était mariée au fils de Adrien de Gerlache, qui a fait le premier hivernage en Antarctique.

Est-ce une vraie rue? Peut-être, mais ça a plutôt l'air d'être un monument, surtout qu'on ne peut qu'y garer sa voiture et il n'y a aucun bâtiment avec cette adresse.

## Rue du 127e Régiment d'Infanterie Française

Mais attends, ce n'est pas si simple. En Wallonie il y a beaucoup de rues qui font référence à des régiments d'infanterie avec leurs numéros. Ici j'ai décidé de ne pas écrire les numéros en toutes lettres<sup>2</sup>, car ça n'est presque jamais fait dans la vie quotidienne. Pourtant, je crois que c'est pertinent d'en tenir compte, parce que ces longs numéros ont un impact sur la prononciation.

J'ai noté la longueur des numéros notés en toutes lettres entre parenthèses dans le tableau. Écrit ainsi, le nom de rue le plus long est sans doute **Rue du Cent Vingt-Septième Régiment d'Infanterie Française**.

Apparemment un nom de rue si long est plutôt embêtant, et par conséquent résumé sur la plaque à **Rue du 127 ième RIF**. Pas si long en fin de compte, hein?

_<sup>2</sup>Ici j'ai utilisé l'abréviation 'e' en suivant les règles [l'Académie Française](https://www.academie-francaise.fr/abreviations-des-adjectifs-numeraux), même si ce n'est pas toujours respecté sur les plaques de rue..._

## Par province
![provincie-moyennes](images/belgie-ingevuld.jpg "Longueur moyenne par province")

[[belgie-ingevuld]] montre que toutes les provinces francophones ont des noms de rue plus longs que les néerlandophones. En soi ce n'est pas illogique, puisque la forme possessive en néerlandais emploie moins de lettres/mots qu’en français.
Prenons, par exemple, **Burgemeester Etienne Demunterlaan** et **Avenue du Bourgmestre Etienne Demunter**: Là où en néerlandais on peut simplement ajouter _“laan”_ à la fin du dernier mot, en français il est souvent nécessaire d'ajouter _“avenue de”_. Par conséquent, même si le mot en lui même est plus court en français, le nom de rue aura au final tout de même plus de caractères: _“rue de la”_ est plus long que _“straat”_ de 3 caractères (espaces compris).

Le gagnant est le Brabant Wallon avec une longueur moyenne de 17.8. Anvers et le Limbourg sont tous deux en bas de la liste, bien que Anvers ait la dernière place avec une longueur moyenne de 13.25 contre 13.28 pour le Limbourg.

## Divers
Enfin, j'ai encore trouvé les plus long noms pour quelques catégories différentes, notamment le plus long nom en un seul mot comme **Tweekleinewegenstraat**, mais même dans cette catégorie cette rue ne se place qu’en 63e place (comme 78 autres rues).


<table>
  <thead>
  <tr>
    <th>Categorie</th>
    <th>Rue</th>
    <th>Place</th>
    <th>Province</th>
  </tr>
  </thead>
  <tbody>
  <tr>
    <td>Sans espaces</td>
    <td>Onze-Lieve-Vrouw-ten-Spiegelestraat</td>
    <td>Courtrai</td>
    <td>Flandre-Occidentale</td>
  </tr>
  <tr>
    <td>1 mot</td>
    <td>Zandvoordeschorredijkstraat</td>
    <td>Ostende</td>
    <td>Flandre-Occidentale</td>
  </tr>
  <tr>
    <td>Le plus de mots</td>
    <td>Rue du 1er Régiment des Chasseurs à Cheval</td>
    <td>Tournai</td>
    <td>Hainaut</td>
  </tr>
  <tr>
    <td></td>
    <td>Chemin du Point de Vue de la Sibérie</td>
    <td>Profondeville</td>
    <td>Namur</td>
  </tr>
  <tr>
    <td></td>
    <td>Cul de Sac de la rue Des Récollets</td>
    <td>Tournai</td>
    <td>Hainaut</td>
  </tr>
  <tr>
    <td>Allemand</td>
    <td>Kelmiser Mühle Mühlenteichweg</td>
    <td>Kelmis</td>
    <td>Liége</td>
  </tr>
  </tbody>
</table>

