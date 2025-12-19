<script setup lang="ts">
const props = defineProps<{
    worldId: number;
    isOpen: boolean;
}>();

const emit = defineEmits(['close', 'created']);

const config = useRuntimeConfig();

const isLoading = ref(false);

// Default Form State
const form = reactive({
    identity: {
        name: '',
        age: 25,
        gender: 'Non-binary',
        occupation: '',
        backstory: '',
    },
    psychology: {
        openness: 0.5,
        conscientiousness: 0.5,
        extraversion: 0.5,
        agreeableness: 0.5,
        neuroticism: 0.5,
    },
    // Simplified defaults for complex nested objects to save UI space for now
    morality: {
        care_harm: 0.5,
        fairness_cheating: 0.5,
        loyalty_betrayal: 0.5,
        authority_subversion: 0.5,
        sanctity_degradation: 0.5,
    },
    emotions: {
        base_mood: 'Calm',
        emotional_volatility: 0.5,
        attachment_style: 'Secure',
        triggers: [],
    },
    cognition: {
        decision_basis: 'Logic',
        impulsivity: 0.3,
    },
    communication: {
        verbosity: 0.5,
        formality: 0.5,
        tone: 'Neutral',
    },
});

const submitAgent = async () => {
    isLoading.value = true;
    try {
        await $fetch(`${config.public.apiUrl}/agents`, {
            method: 'POST',
            body: {
                world_id: props.worldId,
                profile: form,
                initial_situation: 'Just arrived in the world.',
            },
        });
        emit('created');
        emit('close');
        // Reset essential fields
        form.identity.name = '';
        form.identity.occupation = '';
    } catch (e) {
        console.error(e);
        alert('Failed to create agent');
    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
    <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
    >
        <div
            class="h-[80vh] w-200 overflow-hidden rounded-lg border-4 border-amber-800 bg-amber-50
                shadow-2xl"
        >
            <!-- Header -->
            <div class="flex items-center justify-between bg-amber-900 px-6 py-4 text-amber-100">
                <h2 class="font-serif text-2xl font-bold">Create New Lifeform</h2>
                <button @click="$emit('close')" class="hover:text-white">&times;</button>
            </div>

            <!-- Scrollable Form Body -->
            <div class="h-[calc(80vh-8rem)] overflow-y-auto p-6">
                <form @submit.prevent="submitAgent" class="space-y-8">
                    <!-- Section: Identity -->
                    <section>
                        <h3
                            class="mb-4 border-b-2 border-amber-200 pb-1 font-serif text-xl
                                font-bold text-amber-900"
                        >
                            Identity
                        </h3>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-bold text-stone-700">Name</label>
                                <input
                                    v-model="form.identity.name"
                                    type="text"
                                    required
                                    class="w-full rounded border border-stone-300 p-2"
                                />
                            </div>
                            <div>
                                <label class="block text-sm font-bold text-stone-700">Age</label>
                                <input
                                    v-model="form.identity.age"
                                    type="number"
                                    class="w-full rounded border border-stone-300 p-2"
                                />
                            </div>
                            <div>
                                <label class="block text-sm font-bold text-stone-700"
                                    >Occupation</label
                                >
                                <input
                                    v-model="form.identity.occupation"
                                    type="text"
                                    class="w-full rounded border border-stone-300 p-2"
                                />
                            </div>
                            <div>
                                <label class="block text-sm font-bold text-stone-700">Gender</label>
                                <input
                                    v-model="form.identity.gender"
                                    type="text"
                                    class="w-full rounded border border-stone-300 p-2"
                                />
                            </div>
                            <div class="col-span-2">
                                <label class="block text-sm font-bold text-stone-700"
                                    >Backstory</label
                                >
                                <textarea
                                    v-model="form.identity.backstory"
                                    rows="3"
                                    class="w-full rounded border border-stone-300 p-2"
                                ></textarea>
                            </div>
                        </div>
                    </section>

                    <!-- Section: Psychology (Sliders) -->
                    <section>
                        <h3
                            class="mb-4 border-b-2 border-amber-200 pb-1 font-serif text-xl
                                font-bold text-amber-900"
                        >
                            Psychology (Big 5)
                        </h3>
                        <div class="grid grid-cols-1 gap-4">
                            <div
                                v-for="(value, key) in form.psychology"
                                :key="key"
                                class="flex items-center gap-4"
                            >
                                <label class="w-32 text-sm font-bold text-stone-700 capitalize">{{
                                    key
                                }}</label>
                                <input
                                    v-model.number="form.psychology[key]"
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.1"
                                    class="h-2 w-full cursor-pointer appearance-none rounded-lg
                                        bg-stone-300 accent-amber-700"
                                />
                                <span class="w-8 text-right text-sm">{{
                                    form.psychology[key]
                                }}</span>
                            </div>
                        </div>
                    </section>

                    <!-- Submit -->
                    <div class="flex justify-end pt-4">
                        <button
                            type="submit"
                            :disabled="isLoading"
                            class="rounded bg-amber-700 px-6 py-3 font-bold text-white shadow
                                hover:bg-amber-600 disabled:opacity-50"
                        >
                            {{ isLoading ? 'Birthing Agent...' : 'Create Agent' }}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>
