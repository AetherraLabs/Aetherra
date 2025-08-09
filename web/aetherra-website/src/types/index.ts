export interface Plugin {
    id: string;
    name: string;
    description: string;
    version: string;
    author: string;
    status: 'active' | 'beta' | 'experimental';
    downloads: number;
    rating: number;
    category: string;
    tags: string[];
    last_updated: string;
}

export interface CommunityActivity {
    type: string;
    user: string;
    action: string;
    timestamp: string;
    details: string;
}
