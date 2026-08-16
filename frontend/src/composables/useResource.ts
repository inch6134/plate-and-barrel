import { shallowRef, watchEffect } from 'vue'


export const useResource = <T>(load: () => Promise<T>) => {
  const data = shallowRef<T>()
  const error = shallowRef<string>()

  watchEffect(async () => {
    error.value = undefined
    try {
    data.value = await load()
    } catch (failure) {
      error.value = failure instanceof Error ? failure.message : String(failure)
    }
  })

  return { data, error }
}
