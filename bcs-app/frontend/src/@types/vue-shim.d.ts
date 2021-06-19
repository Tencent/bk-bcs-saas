import Vue from 'vue'

declare module 'vue/types/vue' {
    interface Vue {
        PROJECT_CONFIG: {
            doc: any;
            str: any;
        };
        $INTERNAL: boolean;
    }
}
