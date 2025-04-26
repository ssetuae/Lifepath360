import * as React from 'react';
import { Link as RouterLink, LinkProps as RouterLinkProps } from 'react-router-dom';

const ListItemLink = React.forwardRef<HTMLAnchorElement, RouterLinkProps>(function ListItemLink(props, ref) {
  return <RouterLink ref={ref} {...props} role={undefined} />;
});

export default ListItemLink;