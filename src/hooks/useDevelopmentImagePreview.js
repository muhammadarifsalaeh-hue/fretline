import { useSyncExternalStore } from 'react';
import { getDevelopmentImagePreview, getDevelopmentPreviewSnapshot, getEmptyPreviewSnapshot, subscribeDevelopmentPreview } from '@/utils/developmentImagePreview';

const noSubscription = () => () => {};

/** Subscribe only the single preview model; other guitars have no extra state. */
export default function useDevelopmentImagePreview(guitar) {
  const enabled = import.meta.env.DEV && Boolean(getDevelopmentImagePreview(guitar));
  const preview = useSyncExternalStore(enabled ? subscribeDevelopmentPreview : noSubscription,
    enabled ? getDevelopmentPreviewSnapshot : getEmptyPreviewSnapshot, getEmptyPreviewSnapshot);
  return preview?.guitarId === guitar?.id ? preview : null;
}
