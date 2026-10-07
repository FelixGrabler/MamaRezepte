export const categories = ['Suppe', 'Hauptspeise', 'Nachspeise', 'Frühstück', 'sonstiges']

export function tagKey(tag) { return tag.toLocaleLowerCase('de-AT').replaceAll('ß', 'ss') }
