<script setup lang="ts">
defineProps<{ options: { code: string; label: string; count?: number }[]; modelValue: string }>()
defineEmits<{ 'update:modelValue': [code: string] }>()
</script>

<template>
  <nav class="filters">
    <button v-for="option in options" :key="option.code" type="button" :class="{ on: option.code === modelValue }"
      :aria-pressed="option.code === modelValue" @click="$emit('update:modelValue', option.code)">
      {{ option.label }}
      <span v-if="option.count !== undefined" class="count numeric">{{ option.count }}</span>
    </button>
  </nav>
</template>

<style scoped>
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

button {
  padding: 0.38rem 0.8rem;
  background: var(--surface);
  border: 1px solid var(--rule);
  border-radius: 999px;
  font-size: 0.88rem;
  color: var(--ink-2);
  cursor: pointer;
}

button:hover {
  border-color: var(--brown);
  color: var(--brown);
}

button.on {
  background: var(--brown);
  border-color: var(--brown);
  color: var(--surface);
}

.count {
  margin-left: 0.3rem;
  font-size: 0.8rem;
  opacity: 0.7;
}
</style>
