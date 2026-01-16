import { Children, FC, type ReactNode } from 'react'
import ReactMarkdown, { Components } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import rehypeSanitize, { defaultSchema } from 'rehype-sanitize'
import ExpressionText from './ExpressionText'

interface MarkdownMessageProps {
    content: string
}

const MarkdownMessage: FC<MarkdownMessageProps> = ({ content }) => {
    const safeSchema = {
        ...defaultSchema,
        tagNames: Array.from(
            new Set([
                ...(defaultSchema.tagNames || []),
                'p',
                'span',
                'strong',
                'em',
                'code',
                'pre',
                'blockquote',
                'ul',
                'ol',
                'li',
                'h1',
                'h2',
                'h3',
                'h4',
                'h5',
                'h6',
                'br',
                'hr',
            ])
        ),
        attributes: {
            ...defaultSchema.attributes,
            a: [...(defaultSchema.attributes?.a || []), 'target', 'rel'],
            span: [...(defaultSchema.attributes?.span || []), 'className'],
        },
    }

    const renderInline = (children: ReactNode) =>
        Children.map(children, (child) => {
            if (typeof child === 'string') {
                if (
                    child.includes('[[') &&
                    child.includes('::') &&
                    child.includes(']]')
                ) {
                    return <ExpressionText text={child} />
                }
                return child
            }
            return child
        })

    const components: Components = {
        p: ({ children }) => <p>{renderInline(children)}</p>,
        li: ({ children }) => <li>{renderInline(children)}</li>,
        blockquote: ({ children }) => <blockquote>{renderInline(children)}</blockquote>,
        h1: ({ children }) => <h1>{renderInline(children)}</h1>,
        h2: ({ children }) => <h2>{renderInline(children)}</h2>,
        h3: ({ children }) => <h3>{renderInline(children)}</h3>,
        h4: ({ children }) => <h4>{renderInline(children)}</h4>,
        h5: ({ children }) => <h5>{renderInline(children)}</h5>,
        h6: ({ children }) => <h6>{renderInline(children)}</h6>,
        strong: ({ children }) => <strong>{renderInline(children)}</strong>,
        em: ({ children }) => <em>{renderInline(children)}</em>,
        span: ({ children }) => <span>{renderInline(children)}</span>,
        a: ({ href, children }) => (
            <a
                href={href}
                target="_blank"
                rel="noreferrer"
                className="text-indigo-600 underline"
            >
                {renderInline(children)}
            </a>
        ),
        code: (props) => {
            const { inline, children } = props as { inline?: boolean; children?: ReactNode }
            return inline ? (
                <code className="rounded bg-gray-200 px-1 py-0.5 text-xs">
                    {children}
                </code>
            ) : (
                <pre className="overflow-x-auto rounded-lg bg-gray-900 p-3 text-xs text-gray-100">
                    <code>{children}</code>
                </pre>
            )
        },
    }

    return (
        <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeRaw, [rehypeSanitize, safeSchema]]}
            components={components}
        >
            {content}
        </ReactMarkdown>
    )
}

export default MarkdownMessage
