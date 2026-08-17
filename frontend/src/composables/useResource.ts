import { shallowRef, watchEffect } from 'vue'

export const useResource = <T>(load: () => Promise<T>) => {
  const data = shallowRef<T>()
  const error = shallowRef<string>()
  const pending = shallowRef(true)

  /* Every run takes a ticket and only the newest one may write. Switching batters
     quickly fires overlapping requests, and without this the slower of the two
     can land last and leave the panel showing the wrong player. */
  let newest = 0

  watchEffect(async () => {
    const ticket = ++newest
    pending.value = true
    error.value = undefined
    try {
      const loaded = await load()
      if (ticket === newest) {
        data.value = loaded
      }
    } catch (failure) {
      if (ticket === newest) {
        error.value = failure instanceof Error ? failure.message : String(failure)
      }
    }
    if (ticket === newest) {
      pending.value = false
    }
  })

  return { data, error, pending }
}
