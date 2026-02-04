<script lang="ts">
    import {
        Button as ButtonPrimitive,
        type WithoutChildrenOrChild,
    } from "bits-ui";
    import { cn } from "$lib/utils.js";
    import { buttonVariants, type ButtonVariants } from "./index.js";

    let {
        children,
        class: className,
        variant = "default",
        size = "default",
        ref = $bindable(null),
        ...restProps
    }: ButtonPrimitive.RootProps &
        ButtonVariants & { class?: string } = $props();
</script>

<ButtonPrimitive.Root
    bind:ref
    class={cn(buttonVariants({ variant, size, className }))}
    {...restProps}
>
    {@render children?.()}
</ButtonPrimitive.Root>
