<script setup lang="ts">
import type { AgentDetail, AgentProfile } from '~/types/vivarium';

const props = defineProps<{
    worldId: number;
    isOpen: boolean;
    agentToEdit?: AgentDetail | null;
}>();

const emit = defineEmits(['close', 'created', 'updated']);

const { createAgent, updateAgent } = useApi();
const isLoading = ref(false);

const isEditMode = computed(() => !!props.agentToEdit);

// --- Form State ---
const form = reactive<AgentProfile>({
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
        triggers: [] as string[],
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

// --- Populate Form on Edit ---
watch(
    () => props.agentToEdit,
    (agent) => {
        if (agent && agent.profile) {
            Object.assign(form, JSON.parse(JSON.stringify(agent.profile)));
        } else {
            resetForm();
        }
    },
    { immediate: true },
);

function resetForm() {
    form.identity = {
        name: '',
        age: 25,
        gender: 'Non-binary',
        occupation: '',
        backstory: '',
    };
    form.emotions.triggers = [];
}

// --- UI Logic ---
const activeTab = ref('identity');
const tabs = [
    { id: 'identity', label: 'Identity' },
    { id: 'psychology', label: 'Psychology' },
    { id: 'morality', label: 'Morality' },
    { id: 'mind', label: 'Mind & Soul' },
];

const attachmentStyles = [
    'Secure',
    'Anxious-Preoccupied',
    'Dismissive-Avoidant',
    'Fearful-Avoidant',
];
const decisionBases = ['Logic', 'Emotion', 'Intuition', 'Tradition'];

// Trigger Management
const newTrigger = ref('');
const addTrigger = () => {
    const val = newTrigger.value.trim();
    if (val && !form.emotions.triggers.includes(val)) {
        form.emotions.triggers.push(val);
        newTrigger.value = '';
    }
};
const removeTrigger = (index: number) => {
    form.emotions.triggers.splice(index, 1);
};

// --- Event Handling for Game Input ---
const toggleGameInput = (disable: boolean) => {
    window.dispatchEvent(new CustomEvent('vivarium-input-capture', { detail: disable }));
};

watch(
    () => props.isOpen,
    (newVal) => {
        toggleGameInput(newVal);
        if (!newVal) {
            activeTab.value = 'identity';
        }
    },
);

// --- Submission ---
const handleSubmit = async () => {
    isLoading.value = true;
    try {
        if (isEditMode.value && props.agentToEdit) {
            // Update
            await updateAgent(props.agentToEdit.id, form);
            emit('updated');
        } else {
            // Create
            const storedX = localStorage.getItem(`vivarium_pos_x_${props.worldId}`);
            const storedY = localStorage.getItem(`vivarium_pos_y_${props.worldId}`);

            const newAgent = await createAgent({
                world_id: props.worldId,
                profile: form,
                initial_situation: 'Just arrived in the world.',
                x: storedX ? parseFloat(storedX) + 50 : 400,
                y: storedY ? parseFloat(storedY) + 50 : 300,
            });

            window.dispatchEvent(new CustomEvent('vivarium-agent-spawned', { detail: newAgent }));

            emit('created');
            // Only reset on create success
            resetForm();
        }

        emit('close');
    } catch (e) {
        console.error(e);
        alert(`Failed to ${isEditMode.value ? 'update' : 'create'} agent`);
    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
    <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm
            transition-all"
        @keydown.stop
        @keyup.stop
    >
        <div
            class="flex h-[85vh] w-225 flex-col overflow-hidden rounded-xl border-4 border-amber-800
                bg-stone-100 shadow-2xl"
        >
            <!-- Header -->
            <div
                class="flex items-center justify-between border-b-4 border-amber-800 bg-amber-900
                    px-6 py-4 text-amber-50"
            >
                <div class="flex items-center gap-3">
                    <div
                        class="flex h-8 w-8 items-center justify-center rounded-full bg-amber-500
                            font-bold text-amber-900"
                    >
                        {{ isEditMode ? '✎' : '+' }}
                    </div>
                    <h2 class="font-serif text-2xl font-bold tracking-wide">
                        {{ isEditMode ? 'Edit Agent Personality' : 'Construct New Agent' }}
                    </h2>
                </div>
                <button
                    @click="$emit('close')"
                    class="rounded px-2 text-2xl font-bold text-amber-300 hover:bg-amber-800
                        hover:text-white"
                >
                    &times;
                </button>
            </div>

            <!-- Tabs -->
            <div class="flex border-b-2 border-amber-700/30 bg-stone-200">
                <button
                    v-for="tab in tabs"
                    :key="tab.id"
                    @click="activeTab = tab.id"
                    class="flex-1 px-4 py-3 font-serif font-bold transition-colors"
                    :class="
                        activeTab === tab.id
                            ? `bg-stone-100 text-amber-900
                                shadow-[inset_0_-2px_0_0_rgba(120,53,15,1)]`
                            : 'bg-stone-300 text-stone-600 hover:bg-stone-200 hover:text-stone-800'
                    "
                >
                    {{ tab.label }}
                </button>
            </div>

            <!-- Scrollable Form Body -->
            <div class="flex-1 overflow-y-auto bg-stone-100 p-8">
                <form @submit.prevent="handleSubmit" class="mx-auto max-w-3xl space-y-8">
                    <!-- TAB: IDENTITY -->
                    <section
                        v-show="activeTab === 'identity'"
                        class="animate-in fade-in slide-in-from-bottom-2 duration-300"
                    >
                        <div class="grid grid-cols-12 gap-6">
                            <div class="col-span-8">
                                <label class="label">Full Name</label>
                                <input
                                    v-model="form.identity.name"
                                    type="text"
                                    required
                                    placeholder="e.g. Eleanor Vance"
                                    class="input-field"
                                />
                            </div>
                            <div class="col-span-4">
                                <label class="label">Age</label>
                                <input
                                    v-model="form.identity.age"
                                    type="number"
                                    class="input-field"
                                />
                            </div>
                            <div class="col-span-6">
                                <label class="label">Occupation</label>
                                <input
                                    v-model="form.identity.occupation"
                                    type="text"
                                    placeholder="e.g. Quantum Physicist"
                                    class="input-field"
                                />
                            </div>
                            <div class="col-span-6">
                                <label class="label">Gender</label>
                                <input
                                    v-model="form.identity.gender"
                                    type="text"
                                    class="input-field"
                                />
                            </div>
                            <div class="col-span-12">
                                <label class="label">Backstory</label>
                                <textarea
                                    v-model="form.identity.backstory"
                                    rows="6"
                                    placeholder="Describe their history, motivations, and secrets..."
                                    class="input-field resize-none leading-relaxed"
                                ></textarea>
                            </div>
                        </div>
                    </section>

                    <!-- TAB: PSYCHOLOGY -->
                    <section
                        v-show="activeTab === 'psychology'"
                        class="animate-in fade-in slide-in-from-bottom-2 duration-300"
                    >
                        <div
                            class="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm
                                text-amber-900"
                        >
                            The <strong>Big Five</strong> model defines the core personality traits.
                        </div>
                        <div class="space-y-6">
                            <div
                                v-for="(value, key) in form.psychology"
                                :key="key"
                                class="group flex items-center gap-4 rounded-lg border
                                    border-transparent bg-white p-4 shadow-sm transition-all
                                    hover:border-amber-200 hover:shadow-md"
                            >
                                <div class="w-40">
                                    <label
                                        class="block font-serif font-bold text-stone-800 capitalize"
                                    >
                                        {{ key }}
                                    </label>
                                    <span class="text-xs text-stone-500">
                                        {{
                                            key === 'neuroticism'
                                                ? 'Emotional Stability'
                                                : 'Trait Intensity'
                                        }}
                                    </span>
                                </div>
                                <input
                                    v-model.number="
                                        form.psychology[key as keyof typeof form.psychology]
                                    "
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.05"
                                    class="range-slider flex-1"
                                />
                                <div class="w-12 text-right font-mono font-bold text-amber-700">
                                    {{
                                        form.psychology[
                                            key as keyof typeof form.psychology
                                        ].toFixed(2)
                                    }}
                                </div>
                            </div>
                        </div>
                    </section>

                    <!-- TAB: MORALITY -->
                    <section
                        v-show="activeTab === 'morality'"
                        class="animate-in fade-in slide-in-from-bottom-2 duration-300"
                    >
                        <div
                            class="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm
                                text-amber-900"
                        >
                            <strong>Moral Foundations Theory</strong>.
                        </div>
                        <div class="grid grid-cols-1 gap-4">
                            <div
                                v-for="(value, key) in form.morality"
                                :key="key"
                                class="rounded-lg bg-white p-4 shadow-sm"
                            >
                                <div class="mb-2 flex justify-between">
                                    <label class="font-serif font-bold text-stone-800 capitalize">
                                        {{ key.replace('_', ' / ') }}
                                    </label>
                                    <span class="font-mono font-bold text-amber-700">
                                        {{
                                            form.morality[
                                                key as keyof typeof form.morality
                                            ].toFixed(2)
                                        }}
                                    </span>
                                </div>
                                <input
                                    v-model.number="
                                        form.morality[key as keyof typeof form.morality]
                                    "
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.05"
                                    class="range-slider w-full"
                                />
                            </div>
                        </div>
                    </section>

                    <!-- TAB: MIND & SOUL -->
                    <section
                        v-show="activeTab === 'mind'"
                        class="animate-in fade-in slide-in-from-bottom-2 space-y-8 duration-300"
                    >
                        <!-- Emotions -->
                        <div class="rounded-xl border border-stone-200 bg-white p-6 shadow-sm">
                            <h3 class="section-title">Emotional Profile</h3>
                            <div class="grid grid-cols-2 gap-6">
                                <div>
                                    <label class="label">Base Mood</label>
                                    <input
                                        v-model="form.emotions.base_mood"
                                        type="text"
                                        class="input-field"
                                        placeholder="e.g. Melancholic"
                                    />
                                </div>
                                <div>
                                    <label class="label">Attachment Style</label>
                                    <select
                                        v-model="form.emotions.attachment_style"
                                        class="input-field"
                                    >
                                        <option
                                            v-for="style in attachmentStyles"
                                            :key="style"
                                            :value="style"
                                        >
                                            {{ style }}
                                        </option>
                                    </select>
                                </div>
                                <div class="col-span-2">
                                    <div class="mb-1 flex justify-between">
                                        <label class="label">Emotional Volatility</label>
                                        <span class="text-xs font-bold text-amber-700">{{
                                            form.emotions.emotional_volatility
                                        }}</span>
                                    </div>
                                    <input
                                        v-model.number="form.emotions.emotional_volatility"
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        class="range-slider w-full"
                                    />
                                </div>
                                <div class="col-span-2">
                                    <label class="label">Triggers</label>
                                    <div class="mb-2 flex gap-2">
                                        <input
                                            v-model="newTrigger"
                                            @keydown.enter.prevent="addTrigger"
                                            type="text"
                                            placeholder="Type a trigger and press Enter..."
                                            class="input-field flex-1"
                                        />
                                        <button
                                            @click.prevent="addTrigger"
                                            class="rounded bg-stone-200 px-4 font-bold
                                                text-stone-700 hover:bg-stone-300"
                                        >
                                            Add
                                        </button>
                                    </div>
                                    <div class="flex flex-wrap gap-2">
                                        <span
                                            v-for="(trigger, idx) in form.emotions.triggers"
                                            :key="idx"
                                            class="inline-flex items-center gap-1 rounded-full
                                                bg-amber-100 px-3 py-1 text-sm font-bold
                                                text-amber-800"
                                        >
                                            {{ trigger }}
                                            <button
                                                @click="removeTrigger(idx)"
                                                class="ml-1 text-amber-600 hover:text-amber-900"
                                            >
                                                &times;
                                            </button>
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Cognition & Comm -->
                        <div class="grid grid-cols-2 gap-6">
                            <div class="rounded-xl border border-stone-200 bg-white p-6 shadow-sm">
                                <h3 class="section-title">Cognition</h3>
                                <div class="space-y-4">
                                    <div>
                                        <label class="label">Decision Basis</label>
                                        <select
                                            v-model="form.cognition.decision_basis"
                                            class="input-field"
                                        >
                                            <option
                                                v-for="basis in decisionBases"
                                                :key="basis"
                                                :value="basis"
                                            >
                                                {{ basis }}
                                            </option>
                                        </select>
                                    </div>
                                    <div>
                                        <div class="mb-1 flex justify-between">
                                            <label class="label">Impulsivity</label>
                                            <span class="text-xs font-bold text-amber-700">{{
                                                form.cognition.impulsivity
                                            }}</span>
                                        </div>
                                        <input
                                            v-model.number="form.cognition.impulsivity"
                                            type="range"
                                            min="0"
                                            max="1"
                                            step="0.1"
                                            class="range-slider w-full"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div class="rounded-xl border border-stone-200 bg-white p-6 shadow-sm">
                                <h3 class="section-title">Communication</h3>
                                <div class="space-y-4">
                                    <div>
                                        <label class="label">Default Tone</label>
                                        <input
                                            v-model="form.communication.tone"
                                            type="text"
                                            class="input-field"
                                            placeholder="e.g. Sarcastic"
                                        />
                                    </div>
                                    <div>
                                        <div class="mb-1 flex justify-between">
                                            <label class="label">Verbosity</label>
                                            <span class="text-xs font-bold text-amber-700">{{
                                                form.communication.verbosity
                                            }}</span>
                                        </div>
                                        <input
                                            v-model.number="form.communication.verbosity"
                                            type="range"
                                            min="0"
                                            max="1"
                                            step="0.1"
                                            class="range-slider w-full"
                                        />
                                    </div>
                                    <div>
                                        <div class="mb-1 flex justify-between">
                                            <label class="label">Formality</label>
                                            <span class="text-xs font-bold text-amber-700">{{
                                                form.communication.formality
                                            }}</span>
                                        </div>
                                        <input
                                            v-model.number="form.communication.formality"
                                            type="range"
                                            min="0"
                                            max="1"
                                            step="0.1"
                                            class="range-slider w-full"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                </form>
            </div>

            <!-- Footer -->
            <div class="border-t-2 border-stone-300 bg-stone-200 px-8 py-4">
                <div class="flex items-center justify-between">
                    <div class="text-sm text-stone-500 italic">
                        {{
                            isEditMode
                                ? '"People change, even artificial ones."'
                                : '"To simulate life, one must first define the soul."'
                        }}
                    </div>
                    <div class="flex gap-4">
                        <button
                            @click="$emit('close')"
                            class="px-6 py-2 font-bold text-stone-600 transition-colors
                                hover:text-stone-900"
                        >
                            Cancel
                        </button>
                        <button
                            @click="handleSubmit"
                            :disabled="isLoading"
                            class="rounded bg-amber-700 px-8 py-2 font-bold text-white shadow-lg
                                transition-all hover:bg-amber-600 hover:shadow-xl
                                active:translate-y-0.5 disabled:opacity-50"
                        >
                            {{
                                isLoading
                                    ? 'Processing...'
                                    : isEditMode
                                      ? 'Save Changes'
                                      : 'Create Agent'
                            }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
@reference "~/assets/css/main.css";

.label {
    @apply mb-1 block text-xs font-bold tracking-wider text-stone-500 uppercase;
}

.input-field {
    @apply w-full rounded border-2 border-stone-300 bg-stone-50 px-3 py-2 text-stone-800 transition-all outline-none placeholder:text-stone-400 focus:border-amber-500 focus:bg-white focus:ring-2 focus:ring-amber-500/20;
}

.range-slider {
    @apply h-2 cursor-pointer appearance-none rounded-lg bg-stone-300 accent-amber-700 hover:accent-amber-600;
}

.section-title {
    @apply mb-4 border-b border-stone-200 pb-2 font-serif text-lg font-bold text-amber-900;
}
</style>
