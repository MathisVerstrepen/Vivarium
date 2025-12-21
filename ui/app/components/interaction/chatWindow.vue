<script setup lang="ts">
import type { AgentDetail } from '~/types/vivarium';

const props = defineProps<{
    agentId: number | null;
}>();

const emit = defineEmits(['close']);

const { fetchAgentDetailRaw, chatWithAgent } = useApi();

const agent = ref<AgentDetail | null>(null);
const isLoading = ref(false);
const isSending = ref(false);
const playerMessage = ref('');

// We store the session chat locally for display
const chatHistory = ref<Array<{ sender: 'Player' | 'Agent'; text: string; mood?: string }>>([]);
const scrollContainer = ref<HTMLElement | null>(null);

// --- Fetch Agent Details when ID changes ---
const loadAgent = async () => {
    if (!props.agentId) return;
    isLoading.value = true;
    try {
        const data = await fetchAgentDetailRaw(props.agentId);
        agent.value = data;

        chatHistory.value = data.short_term_memory.map((mem) => {
            const [sender, ...msgParts] = mem.split(': ');
            return {
                sender: sender === 'Player' ? 'Player' : 'Agent',
                text: msgParts.join(': '),
            };
        });

        scrollToBottom();
    } catch (e) {
        console.error('Failed to load agent for chat', e);
    } finally {
        isLoading.value = false;
    }
};

watch(() => props.agentId, loadAgent, { immediate: true });

// --- Chat Logic ---
const sendMessage = async () => {
    if (!playerMessage.value.trim() || !agent.value) return;

    const msg = playerMessage.value;
    playerMessage.value = '';

    // Optimistic Update
    chatHistory.value.push({ sender: 'Player', text: msg });
    scrollToBottom();
    isSending.value = true;

    try {
        const res = await chatWithAgent(agent.value.id, msg);

        chatHistory.value.push({
            sender: 'Agent',
            text: res.response.speech,
            mood: res.response.mood,
        });
    } catch (e) {
        chatHistory.value.push({ sender: 'Agent', text: '[Error: Connection Lost]' });
    } finally {
        isSending.value = false;
        scrollToBottom();
    }
};

const scrollToBottom = () => {
    nextTick(() => {
        if (scrollContainer.value) {
            scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
        }
    });
};

// Capture Input when open
watch(
    () => props.agentId,
    (val) => {
        window.dispatchEvent(new CustomEvent('vivarium-input-capture', { detail: !!val }));
    },
);

const closeChat = () => {
    emit('close');
};
</script>

<template>
    <div
        v-if="agentId && agent"
        class="fixed bottom-4 left-1/2 z-50 flex h-125 w-150 -translate-x-1/2 flex-col
            overflow-hidden rounded-xl border-4 border-stone-700 bg-stone-900 shadow-2xl"
        @keydown.stop
        @keyup.stop
    >
        <!-- Header -->
        <div
            class="flex items-center justify-between border-b-2 border-stone-700 bg-stone-800 px-4
                py-3"
        >
            <div class="flex items-center gap-3">
                <div
                    class="flex h-10 w-10 items-center justify-center rounded-full border-2
                        border-amber-500 bg-amber-700 font-bold text-amber-100"
                >
                    {{ agent.name.charAt(0) }}
                </div>
                <div>
                    <h3 class="font-serif text-lg leading-none font-bold text-amber-100">
                        {{ agent.name }}
                    </h3>
                    <span class="text-xs text-stone-400">{{
                        agent.profile.identity.occupation
                    }}</span>
                </div>
            </div>
            <button @click="closeChat" class="text-xl font-bold text-stone-400 hover:text-white">
                &times;
            </button>
        </div>

        <!-- Chat Area -->
        <div ref="scrollContainer" class="flex-1 space-y-4 overflow-y-auto bg-stone-900/90 p-4">
            <div v-if="isLoading" class="mt-10 text-center text-stone-500 italic">
                Connecting to neural link...
            </div>

            <div
                v-for="(msg, index) in chatHistory"
                :key="index"
                class="flex flex-col gap-1"
                :class="msg.sender === 'Player' ? 'items-end' : 'items-start'"
            >
                <div class="mb-0.5 px-1 text-xs font-bold text-stone-500 uppercase">
                    {{ msg.sender === 'Player' ? 'You' : agent.name }}
                    <span v-if="msg.mood" class="ml-1 text-amber-500">({{ msg.mood }})</span>
                </div>
                <div
                    class="max-w-[80%] rounded-2xl px-4 py-2 text-sm leading-relaxed"
                    :class="
                        msg.sender === 'Player'
                            ? 'rounded-tr-none bg-amber-700 text-white'
                            : 'rounded-tl-none border border-stone-600 bg-stone-700 text-stone-200'
                    "
                >
                    {{ msg.text }}
                </div>
            </div>

            <div
                v-if="isSending"
                class="flex animate-pulse items-center gap-2 text-xs text-stone-500 italic"
            >
                <span>{{ agent.name }} is thinking...</span>
            </div>
        </div>

        <!-- Input Area -->
        <div class="border-t-2 border-stone-700 bg-stone-800 p-3">
            <form @submit.prevent="sendMessage" class="flex gap-2">
                <input
                    v-model="playerMessage"
                    type="text"
                    placeholder="Type a message..."
                    class="flex-1 rounded-lg border border-stone-600 bg-stone-900 px-4 py-2
                        text-stone-200 focus:border-amber-500 focus:ring-1 focus:ring-amber-500
                        focus:outline-none"
                    :disabled="isSending"
                />
                <button
                    type="submit"
                    :disabled="!playerMessage || isSending"
                    class="rounded-lg bg-amber-600 px-4 py-2 font-bold text-white transition-colors
                        hover:bg-amber-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    Send
                </button>
            </form>
        </div>
    </div>
</template>
