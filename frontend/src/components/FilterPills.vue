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
  padding: 0.3rem 0.6rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 999px;
  font-size: 0.78rem;
  cursor: pointer;
}

button.on {
  background: var(--brown);
  border-color: var(--brown);
  color: var(--paper);
}

.count {
  margin-left: 0.3rem;
  font-size: 0.7rem;
  opacity: 0.6;
}
</style>
