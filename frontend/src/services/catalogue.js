export const categories = ['Suppe', 'Hauptspeiße', 'Nachspeiße', 'Frühstück', 'sonstiges']

export function tagKey(tag) { return tag.toLocaleLowerCase('de-AT').replaceAll('ß', 'ss') }
