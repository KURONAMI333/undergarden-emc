# Changelog

## v0.1.0

Initial release.

- ProjectE EMC integration for The Undergarden (NeoForge 1.21.1 and Forge 1.20.1).
- Hand-set EMC on 64 ids for 1.21.1 and 52 ids for 1.20.1; ProjectE derives the rest from the host mod's vanilla-type recipes.
- Metal EMC lives on ingots. Ore blocks and raw chunks stay at zero, so depthrock, dreadrock, shiverstone and tremblecrust cannot become separate price entrances to one metal.
- The four Infuser recipes are declared as explicit conversions on 1.21.1, counting the consumed catalyst. The Undergarden for 1.20.1 has no Infuser.
- The five music discs are valued at 2,048 each on 1.21.1, matching the vanilla tier ProjectE prices; on 1.20.1 they already inherit that value from ProjectE's disc tag.
- Carved gloomgourds, gloom-o-lanterns and shard-o-lanterns intentionally left without EMC: shearing a placed gloomgourd yields a carved gloomgourd plus four seeds, which would otherwise repeat EMC.
- Tools, weapons and armour intentionally left without EMC (durability and enchantments are item state).
- Depthrock variants dropping vanilla iron, gold, diamond or coal are left untouched so vanilla's existing EMC band is unchanged.
- Data-only: adds no items, blocks or recipes. Server-side; clients do not need it.
