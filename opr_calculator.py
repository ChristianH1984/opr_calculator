from typing import List
from collections import defaultdict


class Modifier():
    def __init__(self, name=str, modifier=None):
        self.modifier = modifier
        self.name = name

    def __str__(self):
        return self.name

    def modify_hits(self, hits, **kwargs):
        return hits

    def modify_wounds(self, wounds, **kwargs):
        return wounds

    def modify_quality(self, quality, **kwargs):
        return quality

    def modifiy_defense(self, defense, **kwargs):
        return defense

    def modify_ap(self, ap, **kwargs):
        return ap


class Sniper(Modifier):

    def modify_quality(self, quality, **kwargs):
        return self.modifier


class Reliable(Sniper):
    pass


class Blast(Modifier):

    def modify_hits(self, hits, **kwargs):
        if kwargs['mode'] == 'attack':
            return min(self.modifier * hits, kwargs['unit'].n_models)
        else:
            return hits


class Rending(Modifier):
    def modify_ap(self, ap, **kwargs):
        if kwargs['mode'] == 'attack':
            return 5. / 6. * ap + 1. / 6. * 4
        else:
            return ap
    # regen modifier missing


class Regeneration(Modifier):
    def modify_wounds(self, wounds, **kwargs):
        if kwargs['mode'] == 'defend':
            return wounds * ((5. - 1.) / 6.)
        else:
            return wounds


class Deadly(Modifier):
    def modify_wounds(self, wounds, **kwargs):
        if kwargs['mode'] == 'attack':
            return min(self.modifier, kwargs['unit'].tough) * wounds
        return wounds


class Special():
    def __init__(self, modifiers: List[Modifier] = list()):
        self.modifiers = modifiers

    def __str__(self):
        return ", ".join([str(mod) for mod in self.modifiers])

    def modify_hits(self, hits, **kwargs):
        for modifier in self.modifiers:
            hits = modifier.modify_hits(hits, **kwargs)
        return hits

    def modify_wounds(self, wounds, **kwargs):
        for modifier in self.modifiers:
            wounds = modifier.modify_wounds(wounds, **kwargs)
        return wounds

    def modify_quality(self, quality, **kwargs):
        for modifier in self.modifiers:
            quality = modifier.modify_quality(quality, **kwargs)
        return quality

    def modify_defense(self, defense, **kwargs):
        for modifier in self.modifiers:
            defense = modifier.modify_defense(defense, **kwargs)
        return defense


class Weapon:
    def __init__(self, name, attacks, ap, special=Special(), points=0):
        self.name = name
        self.attacks = attacks
        self.ap = ap
        self.special = special
        self.points = points

    def __str__(self):
        return f"{self.name}, Attacks {self.attacks}, AP {self.ap}, Special {self.special} Points: {self.points}"


class Unit():
    def __init__(self, name, n_models, quality, defense, points, tough=1, special=Special()):
        self.equipment = []
        self.name = name
        self.n_models = n_models
        self.tough = tough
        self.quality = quality
        self.defense = defense
        self.points = points
        self.special = special

    def equip(self, weapons: List[Weapon]):
        self.equipment += weapons
        for weapon in weapons:
            self.points += weapon.points


class Attack:

    @staticmethod
    def fight(unit1, unit2):
        rounds = 4
        hits_total = 0
        wounds_total = 0
        results = {}
        for equipment in unit1.equipment:
            if isinstance(equipment, Weapon):
                quality = equipment.special.modify_quality(unit1.quality, mode='attack')
                n_hits = equipment.special.modify_hits(equipment.attacks * (1 - (quality - 1) / 6.0), mode='attack',
                                                       unit=unit2)
                wounds = unit2.special.modify_wounds(
                    equipment.special.modify_wounds(n_hits * min((unit2.defense - 1 + equipment.ap) / 6.0, 5.0 / 6.0),
                                                    unit=unit2, mode='attack'), mode='defend', unit=unit1)

                hits_total += n_hits
                wounds_total += wounds
                print(f"{equipment.name}: {n_hits*rounds} hits causing {wounds*rounds}")
                results[equipment.name] = {"hits": f"{n_hits * rounds:.{2}f}", "wounds": f"{wounds * rounds:.{2}f}", "wounds in enemy points": f"{wounds / (unit2.tough * unit2.n_models) * unit2.points:.{2}f}"}
        points = wounds_total / (unit2.tough * unit2.n_models) * unit2.points
        results['Complete'] = {"hits": f"{hits_total * rounds:.{2}f}", "wounds": f"{wounds_total * rounds:.{2}f}", "wounds in enemy points": f"{points * rounds:.{2}f}", "points_ratio [damage inflicted versus unit costs]": f"{(points * rounds) / unit1.points:.{2}f}"}
        return results
