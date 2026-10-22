/** Optional sourced fields: absent keys never add rows to another guitar. */
export const ADDITIONAL_SPECIFICATIONS = [
  { key: 'series', label: 'spec.series', group: 'construction', type: 'text' },
  { key: 'bodyShape', label: 'spec.bodyShape', group: 'construction', type: 'text' },
  { key: 'neckFinish', label: 'spec.neckFinish', group: 'construction', type: 'text' },
  { key: 'fingerboardRadiusMm', label: 'spec.fingerboardRadius', group: 'construction', type: 'number', unit: ' mm' },
  { key: 'nut', label: 'spec.nut', group: 'construction', type: 'text' },
  { key: 'pickupConfiguration', label: 'spec.pickupConfiguration', group: 'electronics', type: 'text' },
  { key: 'bridgePickup', label: 'spec.bridgePickup', group: 'electronics', type: 'text' },
  { key: 'middlePickup', label: 'spec.middlePickup', group: 'electronics', type: 'text' },
  { key: 'neckPickup', label: 'spec.neckPickup', group: 'electronics', type: 'text' },
  { key: 'pickupSelector', label: 'spec.pickupSelector', group: 'electronics', type: 'text' },
  { key: 'tuners', label: 'spec.tuners', group: 'details', type: 'text' },
];
