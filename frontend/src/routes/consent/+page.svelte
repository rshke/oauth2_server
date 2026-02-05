<script lang="ts">
    import { Button } from "$lib/components/ui/button";
    import {
        Card,
        CardContent,
        CardDescription,
        CardFooter,
        CardHeader,
        CardTitle,
    } from "$lib/components/ui/card";
    import { Label } from "$lib/components/ui/label";
    import { Checkbox } from "$lib/components/ui/checkbox"; // Assuming checkbox exists, if not I'll check or remove
</script>

<div class="flex items-center justify-center min-h-screen bg-gray-100">
    <Card class="w-[450px]">
        <CardHeader>
            <CardTitle>Authorize Application</CardTitle>
            <CardDescription>
                <strong>Example App</strong> wants to access your account.
            </CardDescription>
        </CardHeader>
        <CardContent>
            <div class="flex flex-col space-y-4">
                <p class="text-sm text-gray-500">
                    The application is requesting the following permissions:
                </p>
                <div class="flex items-center space-x-2">
                    <!-- Placeholder for permissions/scopes -->
                    <!-- If checkbox component exists use it, otherwise simple input or stylized div -->
                    <div
                        class="space-y-2 border p-4 rounded-md w-full bg-white"
                    >
                        <div class="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                id="scope1"
                                checked
                                disabled
                                class="accent-primary"
                            />
                            <Label for="scope1">Read your profile</Label>
                        </div>
                        <div class="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                id="scope2"
                                checked
                                disabled
                                class="accent-primary"
                            />
                            <Label for="scope2">Access your email</Label>
                        </div>
                    </div>
                </div>
            </div>
        </CardContent>
        <CardFooter class="flex justify-between">
            <Button variant="ghost">Deny</Button>
            <Button>Allow Access</Button>
        </CardFooter>
    </Card>
</div>
